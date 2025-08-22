from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import OpenAI, ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate

from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


import os
import json
from dotenv import load_dotenv
load_dotenv()

import asyncio

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages:Annotated[list,add_messages]

class EncompassDevConnectAgent():
    name = "EncompassDevConnectAgent"
    description = "This agent retrieves data from Encompass system using DevConnect APIs"

    async def arun(self, user_query:str)->State:
        # create model
        llm=ChatOpenAI(model=os.getenv('OPENAI_LLM_MODEL'),api_key=os.getenv('OPENAI_API_KEY'))

        # create mcp client with each server
        mcp_client=MultiServerMCPClient(
            {
                "Math": {
                    "command": "python",
                    # Make sure to update to the full absolute path to your math_server.py file
                    "args": ["mathserver.py"],
                    "transport": "stdio",
                },
                "Weather": {
                    # Make sure you start your weather server on port 8000
                    "url": "http://127.0.0.1:8000/mcp",
                    "transport": "streamable_http",
                },
                "EncompassApiDocumentation": {
                    # Make sure you start your FetchEncompassApiAuthToken server on port 8001
                    "url": "http://127.0.0.1:8001/mcp",
                    "transport": "streamable_http",
                },
                "FetchEncompassApiAuthToken": {
                    # Make sure you start your FetchEncompassApiAuthToken server on port 8002
                    "url": "http://127.0.0.1:8002/mcp",
                    "transport": "streamable_http",
                },
                "FetchEncompassLoans": {
                    # Make sure you start your FetchEncompassLoans server on port 8003
                    "url": "http://127.0.0.1:8003/mcp",
                    "transport": "streamable_http",
                },
            }
        )

        # all_tools=await mcp_client.get_tools()
        # Example: explicitly starting a session
        # from langchain_mcp_adapters.client import MultiServerMCPClient
        # from langchain_mcp_adapters.tools import load_mcp_tools
        # client = MultiServerMCPClient({...})
        # async with client.session("math") as session:
        #     tools = await load_mcp_tools(session)
        #     }
        # )
        all_tools=await mcp_client.get_tools()

        # Python dictionary representing JSON data
        match_criteria_sample_json = {
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
        }

        # Convert the Python dictionary to a JSON string
        match_criteria_sample_json_string = json.dumps(match_criteria_sample_json)

        system_prompt = """
        You are an expert at Encompass Developer Connect API Catalog, and expert in retrieving loan data by making API calls to get loan pipeline.

        If user requests for loans based on match criteria, first identify appropriate api url based on documentation, second retrieve bearer access_token, third build the filter json payload based on documentation, then finally make API call and respond with JSON data.
        
        When user asks for Investment property or Primary home or Secondary home add field Fields.1811 to the filter appropriately.
        
        When user refer to Conventional or FHA or USDA or VA loans, add field Fields.1172 to the filter appropriately.

        When user refer to Credit score or FICO score in the query, add field Fields.2853 to the filter appropriately.

        When user refer to borrower name in the query, add field Loan.BorrowerName to the filter appropriately.

        When requesting for fields in response always request for Fields.GUID, Fields.364, Loan.BorrowerName, Fields.1109, Fields.1393, Fields.LOANLASTMODIFIED, Fields.1172, Fields.1811, Fields.2853, Fields.1041.

        Build the match criteria yourself based on the api documentation, for your reference here is a sample match criteria JSON:
        {match_criteria_sample_json}

        Always let the user know when you didn't find the loans - be honest.
        """
        
        # format
        # system_prompt_formatted = system_prompt.format(match_criteria_sample_json_string)

        # system prompt
        # prompt = PromptTemplate(template=system_prompt, input_variables=[match_criteria_sample_json_string])

        prompt_template = PromptTemplate(
            input_variables=["match_criteria_sample_json"],
            template=system_prompt
        )

        # Correct: Providing the expected variables when invoking or formatting
        formatted_prompt = prompt_template.format(match_criteria_sample_json=match_criteria_sample_json_string)

        # create react agent
        agent=create_react_agent(
            llm, 
            all_tools,
            prompt=formatted_prompt
        )

        # invoke agent
        tool_response= await agent.ainvoke(
            {"messages": [{"role":"user","content":user_query}]}
        )
        # print("tool_response", tool_response['messages'][-1].content)

        # return response
        return tool_response
    
