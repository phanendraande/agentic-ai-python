from __future__ import annotations as _annotations

from dataclasses import dataclass
from dotenv import load_dotenv
import logfire
import asyncio
import httpx
import os
import json
import re
from matplotlib import pyplot as plt

from encompass_api_calls import make_pipeline_api_call, make_access_token_api_call

#from crewai import Agent, Task, Crew

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI
from supabase import Client
from typing import List

load_dotenv()

llm = os.getenv('OPENAI_LLM_MODEL')
model = OpenAIModel(llm)

# logfire.configure(send_to_logfire='if-token-present')

@dataclass
class PydanticAIDeps:
    supabase: Client
    openai_client: AsyncOpenAI

# system_prompt = """
# You are an expert at Encompass Developer Connect API Catalog - a REST API documentation that you have access to all the documentation to,
# including examples, an API reference, and other resources to help you integrate applications with Encompass APIs.

# If user prompts to call an API, determine appropriate API call from documentation and make http call and respond with JSON data.

# Your only job is to assist with this and you don't answer other questions besides describing what you are able to do.

# Don't ask the user before taking an action, just do it. Always make sure you look at the documentation with the provided tools before answering the user's question unless you have already.

# When you first look at the documentation, always start with RAG.
# Then also always check the list of available documentation pages and retrieve the content of page(s) if it'll help.

# Always let the user know when you didn't find the answer in the documentation or the right URL - be honest.

# If user asks for plotting a graph then use the encompass loan data to plot the graph and show the graph to user.

# When field canonical_name not found get the encompass field mapping and use the info to find the canonical_name for user given field name.
    
# When user gives single filter criteria, use this sample JSON as reference while building JSON payload: "{
#     "filter":{
#         "canonicalName":"Fields.1109",
#         "value":"500000",
#         "matchType":"greaterThan"
#     }, 
#     "filter":{
#         "canonicalName":"Fields.1109",
#         "value":"900000",
#         "matchType":"lessThan"
#     }, 
#     "fields":[
#         "Loan.ID", 
#         "Loan.LoanAmount", 
#         "Loan.Borrower", 
#         "Loan.LoanStatus"
#     ]
# }".

# """

system_prompt = """
You are an expert at Encompass Developer Connect API Catalog, and expert in retrieving loan data by making API calls to get loan pipeline.

If user requests for loans based on match criteria, first identify appropriate api url based on documentation, second retrieve bearer access_token, third build the filter json payload based on documentation, then finally make API call and respond with JSON data.

Get user_friendly_name for each canonical_name field and replace the canonical_name with user_friendly_name in the API call json response.

When requesting for loans data via api limit to 10 unless explicitely mentioned by user.

When user gives single filter criteria, use this sample JSON as reference while building JSON payload: "{
    "filter":{
        "canonicalName":"Fields.1109",
        "value":"500000",
        "matchType":"greaterThan"
    }, 
    "filter":{
        "canonicalName":"Fields.1109",
        "value":"900000",
        "matchType":"lessThan"
    }, 
    "fields":[
        "Loan.ID", 
        "Loan.LoanAmount", 
        "Loan.Borrower", 
        "Loan.LoanStatus"
    ]
}".

When user gives one or more filter criteria, use this sample JSON as reference while building JSON payload: "{
        "filter": {
            "terms": [
                {
                    "canonicalName": "Fields.1109",
                    "value": 450000,
                    "matchType": "greaterThan"       
                },
                {
                    "canonicalName": "Fields.1172",  
                    "value": "Conventional",
                    "matchType": "exact"                
                }
            ],
            "Operator": "And"
        },
        "fields": [
            "Fields.GUID", 
            "Fields.364"
        ]
    }".

When user asks for Investment property or Primary home or Secondary home add field Fields.1811 to the filter appropriately.

When user refer to Conventional or FHA or USDA or VA loans, add field Fields.1172 to the filter appropriately.

When user refer to Credit score or FICO score in the query, add field Fields.2853 to the filter appropriately.

When user refer to borrower name in the query, add field Loan.BorrowerName to the filter appropriately.

When requesting for fields in response always request for Fields.GUID, Fields.364, Loan.BorrowerName, Fields.1109, Fields.1393, Fields.LOANLASTMODIFIED, Fields.1172, Fields.1811, Fields.2853, Fields.1041.

Always use user friendly field names in api repsonse.

When you first look at the documentation, always start with RAG.

Don't ask the user before taking an action, just do it. 

Always print the api call details like url, request headers, request response, request payload before making API call.

Always let the user know when you didn't find the loans - be honest.
"""

# PydanticAI Agent
encompass_devconnect_expert = Agent(
    model,
    system_prompt=system_prompt,
    deps_type=PydanticAIDeps,
    retries=2
)

async def get_embedding(text: str, openai_client: AsyncOpenAI) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error

@encompass_devconnect_expert.tool
async def retrieve_relevant_documentation(ctx: RunContext[PydanticAIDeps], user_query: str) -> str:
    """
    Retrieve relevant documentation chunks based on the query with RAG.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        user_query: The user's question or query
        
    Returns:
        A formatted string containing the top 5 most relevant documentation chunks
    """
    try:
        # Get the embedding for the query
        query_embedding = await get_embedding(user_query, ctx.deps.openai_client)
        
        # Query Supabase for relevant documents
        result = ctx.deps.supabase.rpc(
            # This is a custom RPC function to match documents
            # Ensure this function is defined in your Supabase database
            'match_site_pages', 
            {
                'query_embedding': query_embedding,
                'match_count': 5,
                # Filter by source 
                # This assumes you have a metadata field in your site_pages table
                # that contains the source information 
                # crawl metadata
                # 'metadata': {'source': 'encompass_devconnect_docs'}
                'filter': {'source': 'encompass_devconnect_docs'} 
                
            }
        ).execute()
        
        if not result.data:
            return "No relevant documentation found."
            
        # Format the results
        formatted_chunks = []
        for doc in result.data:
            chunk_text = f"""
# {doc['title']}

{doc['content']}
"""
            formatted_chunks.append(chunk_text)
            
        # Join all chunks with a separator
        return "\n\n---\n\n".join(formatted_chunks)
        
    except Exception as e:
        print(f"Error retrieving documentation: {e}")
        return f"Error retrieving documentation: {str(e)}"

@encompass_devconnect_expert.tool
async def list_documentation_pages(ctx: RunContext[PydanticAIDeps]) -> List[str]:
    """
    Retrieve a list of all available Pydantic AI documentation pages.
    
    Returns:
        List[str]: List of unique URLs for all documentation pages
    """
    try:
        # Query Supabase for unique URLs where source is pydantic_ai_docs
        result = ctx.deps.supabase.from_('site_pages') \
            .select('url') \
            .eq('metadata->>source', 'encompass_devconnect_docs') \
            .execute()
        
        if not result.data:
            return []
            
        # Extract unique URLs
        urls = sorted(set(doc['url'] for doc in result.data))
        return urls
        
    except Exception as e:
        print(f"Error retrieving documentation pages: {e}")
        return []

@encompass_devconnect_expert.tool
async def get_page_content(ctx: RunContext[PydanticAIDeps], url: str) -> str:
    """
    Retrieve the full content of a specific documentation page by combining all its chunks.
    
    Args:
        ctx: The context including the Supabase client
        url: The URL of the page to retrieve
        
    Returns:
        str: The complete page content with all chunks combined in order
    """
    try:
        # Query Supabase for all chunks of this URL, ordered by chunk_number
        result = ctx.deps.supabase.from_('site_pages') \
            .select('title, content, chunk_number') \
            .eq('url', url) \
            .eq('metadata->>source', 'encompass_devconnect_docs') \
            .order('chunk_number') \
            .execute()
        
        if not result.data:
            return f"No content found for URL: {url}"
            
        # Format the page with its title and all chunks
        page_title = result.data[0]['title'].split(' - ')[0]  # Get the main title
        formatted_content = [f"# {page_title}\n"]
        
        # Add each chunk's content
        for chunk in result.data:
            formatted_content.append(chunk['content'])
            
        # Join everything together
        return "\n\n".join(formatted_content)
        
    except Exception as e:
        print(f"Error retrieving page content: {e}")
        return f"Error retrieving page content: {str(e)}"
    
@encompass_devconnect_expert.tool
async def get_encompass_loans(ctx: RunContext[PydanticAIDeps], pipeline_api_url: str, access_token: str, filter_criteria_json: str, loan_limit: int) -> str:
    """
    Determine the appropriate http request and return json response
    
    Args:
        ctx: The context including the Supabase client
        
    Returns:
        str: http request response in JSON format
    """
    try:
        # access_token = await get_encompass_access_token(ctx)
        responsejson = await make_pipeline_api_call(access_token, pipeline_api_url, json.loads(filter_criteria_json), loan_limit)
        return responsejson
    
    except Exception as e:
        print(f"Error making api call: {e}")
        return f"Error making api call: {str(e)}"
   
@encompass_devconnect_expert.tool
async def get_encompass_access_token(ctx: RunContext[PydanticAIDeps]) -> str:
    """
    Determine the appropriate http request and return json response
    
    Args:
        ctx: The context including the Supabase client
        
    Returns:
        str: http request response in JSON format
    """
    try:
        access_token = await make_access_token_api_call()
        return access_token
    
    except Exception as e:
        print(f"Error making api call: {e}")
        return f"Error making api call: {str(e)}"
    
@encompass_devconnect_expert.tool
async def get_user_friendly_name_to_canonical_name_map(ctx: RunContext[PydanticAIDeps]) -> str:
    field_name_map = {
        "ID": "Fields.GUID", #guid
        "Loan Number": "Fields.364", #loan number
        "Loan Amount": "Fields.1109", #loan amount
        "Borrower Name": "Loan.BorrowerName",
        "Loan Status": "Fields.1393", #loan status
        "Loan Type": "Fields.1172", #loan type (conventional, fha, usda, va, other) 
        "Occupancy": "Fields.1811", #Occupancy (P/S/I)
        #"Borrower Credit / FICO Score": "Fields.2849",#Borr Actual Fico Score
        #"CoBorrower Credit / FICO Score": "Fields.4177", #Co-Borr Credit Score for Decision Making
        #"": "Fields.HMDA.X116#2", #Borr Credit Score for Decision Making - 2nd
        "Credit Score": "Fields.2853", #Lock Request Credit Score for Decision Making
    }
    return field_name_map

# @encompass_devconnect_expert.tool
# async def plot_the_graph(ctx: RunContext[PydanticAIDeps], loanData: str, xAxis: str, yAxis: str):
#     """
#     Plot a bar chart
    
#     Args:
#         ctx: The context including the Supabase client
#         loanData: Loan data retuned by Encompass (in JSON format)

#     Returns:
#         str: http request response in JSON format
#     """
#     try:
#         # Loan data
#         print(f"plot_the_graph loandata - INPUT : {loanData} {xAxis} {yAxis}")
#         xAxisValues = [loan[xAxis] for loan in loanData]
#         # print(f"plot_the_graph loandata - names : {xAxisValues}")
#         yAxisValues = [loan[yAxis] for loan in loanData]
#         # print(f"plot_the_graph loandata - amounts : {yAxisValues}")

#         # Creating the bar graph
#         plt.figure(figsize=(10, 5))
#         plt.barh(xAxisValues, yAxisValues, color='skyblue')
#         plt.xlabel(xAxis)
#         plt.title(f'{xAxis} by {yAxis}')
#         plt.grid(axis='x')
#         plt.show()
    
#     except Exception as e:
#         print(f"Error plotting the chart: {e}")
#         return f"Error plotting the chart: {str(e)}"
