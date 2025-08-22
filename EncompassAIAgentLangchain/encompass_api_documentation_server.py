# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP
from openai import AsyncOpenAI
from supabase import Client
from typing import List

import os
from dotenv import load_dotenv
load_dotenv()

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase: Client = Client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

mcp_documentation=FastMCP("EncompassApiDocumentation")

@mcp_documentation.tool()
async def retrieve_relevant_documentation(user_query: str) -> str:
    """
    Retrieve relevant documentation chunks based on the query with RAG.
    
    Args:
        user_query: The user's question or query
        
    Returns:
        A formatted string containing the top 5 most relevant documentation chunks
    """
    try:
        # Get the embedding for the query
        query_embedding = await get_embedding(user_query)
        
        # Query Supabase for relevant documents
        result = supabase.rpc(
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

@mcp_documentation.tool()
async def list_documentation_pages() -> List[str]:
    """
    Retrieve a list of all available Pydantic AI documentation pages.
    
    Returns:
        List[str]: List of unique URLs for all documentation pages
    """
    try:
        # Query Supabase for unique URLs where source is pydantic_ai_docs
        result = supabase.from_('site_pages') \
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

@mcp_documentation.tool()
async def get_page_content(url: str) -> str:
    """
    Retrieve the full content of a specific documentation page by combining all its chunks.
    
    Args:
        url: The URL of the page to retrieve
        
    Returns:
        str: The complete page content with all chunks combined in order
    """
    try:
        # Query Supabase for all chunks of this URL, ordered by chunk_number
        result = supabase.from_('site_pages') \
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
    
async def get_embedding(text: str) -> List[float]:
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
    

# if __name__=="__main__":
#     mcp_documentation.run(transport="streamable-http")

if __name__ == "__main__":
    mcp_documentation.run(
        transport="streamable-http",  # Use "http" for Streamable HTTP
        host="127.0.0.1",  # Listen on all available interfaces
        port=8001,         # Specify your desired port
        # endpoint="/mcp"    # Optional: Customize the endpoint path
    )