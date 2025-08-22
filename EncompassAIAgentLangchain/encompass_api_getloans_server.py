# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP

import requests
import os
import datetime 
import json

from dotenv import load_dotenv
load_dotenv()

mcp_getloans=FastMCP("FetchEncompassLoans")

@mcp_getloans.tool()
async def get_encompass_loans(pipeline_api_url: str, access_token: str, filter_criteria_json: str, loan_limit: int) -> str:
    """
    Determine the appropriate http request and return json response
    
    Args:
        pipeline_api_url: api url for which the HTTP request need to be made
        access_token: auth token to access api
        filter_criteria_json: the filter json that will be used to filter the loans
        loan_limit: number of loans that need to fetched and sent in api request url

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
    
async def make_pipeline_api_call(encompass_access_token: str, api_url: str, filter_criteria_json: any, loan_limit: int) -> str:
    """
    Make the actual api call and get the response
    
    Args:
        encompass_access_token: api access / auth token
        api_url: api url for which the HTTP request need to be made
        filter_criteria_json: the filter json that will be used to filter the loans
        loan_limit: number of loans that need to fetched and sent in api request url

    Returns:
        str: http request response in JSON format
    """
    try:
        # Define the API endpoint
        url = f"{api_url}{loan_limit}"

        # Set your headers (replace 'YOUR_ACCESS_TOKEN' with your actual access token)
        headers = {
            "Authorization": f"Bearer {encompass_access_token}",
            "content-Type": "application/json",
            "accept": "application/json"
        }
        
        # print(f"make_pipeline_api_call - url: {url}")
        # print(f"make_pipeline_api_call - payload: {filter_criteria_json}")

        # Make the POST request
        response = requests.post(url, headers=headers, json=filter_criteria_json)

        # Check the response
        if response.status_code == 200:
            print("Successfully retrieved Loans::")
            return response.json()
        else:
            print("Error:", response.status_code, response.text) 

    except Exception as e:
        print(f"Error making encompass api call: {e}")
        return ""


# if __name__=="__main__":
#     mcp_getloans.run(transport="streamable-http")

if __name__ == "__main__":
    mcp_getloans.run(
        transport="streamable-http",  # Use "http" for Streamable HTTP
        host="127.0.0.1",  # Listen on all available interfaces
        port=8003,         # Specify your desired port
        # endpoint="/mcp"    # Optional: Customize the endpoint path
    )