import requests
import os
import json
import base64
import asyncio
import functools
import time
import datetime 
import re
from matplotlib import pyplot as plt

from dotenv import load_dotenv

load_dotenv()

async def make_pipeline_api_call(encompass_access_token: str, api_url: str, filter_criteria_json: any, loan_limit: int) -> str:
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
    
async def make_fieldnames_api_call(encompass_access_token: str) -> str:
    try:
        # Define the API endpoint
        url = "https://api.elliemae.com/encompass/v1/loanPipeline/fieldDefinitions"
        # encompass_access_token = os.getenv("ENCOMPASS_BEARER_TOKEN")

        # Set your headers (replace 'YOUR_ACCESS_TOKEN' with your actual access token)
        headers = {
            "Authorization": f"Bearer {encompass_access_token}",
            "content-Type": "application/json",
            "accept": "application/json"
        }
        print(headers)
        # Make the GET request
        response = requests.get(url, headers=headers)

        # Check the response
        if response.status_code == 200:
            print("Successfully retrieved field names::")
            return response.json()
        else:
            print("Error:", response.status_code, response.text) 

    except Exception as e:
        print(f"Error making encompass api call: {e}")
        return ""
    
# @functools.lru_cache(maxsize=1)
async def make_access_token_api_call() -> str:
    try:
        # return "0004RewpLsVXTxcpdQka6aCOXwYO"
        # Define the API endpoint
        # url = authurl
        
        # instance_id=os.getenv("ENCOMPASS_INSTANCE_ID")
        # user_id=os.getenv("ENCOMPASS_USER_ID")
        # user_pwd=os.getenv("ENCOMPASS_USER_PWD")
        # api_cleint_id=os.getenv("ENCOMPASS_API_CLIENT_ID")
        # api_cleint_secret=os.getenv("ENCOMPASS_API_CLIENT_SECRET")

        url = "https://api.elliemae.com/oauth2/v1/token"
        instance_id = os.getenv("ENCOMPASS_INSTANCE_ID")
        client_id = os.getenv("ENCOMPASS_API_CLIENT_ID")
        client_secret = os.getenv("ENCOMPASS_API_CLIENT_SECRET")
        username = f"{os.getenv("ENCOMPASS_USER_ID")}@encompass:{instance_id}" #user_name@encompass:{{encompass_instance_id}}.
        password = os.getenv("ENCOMPASS_USER_PWD")

        # # Prepare basic authentication credentials
        # auth_string = f"{username}:{password}"
        # encoded_auth_string = base64.b64encode(auth_string).encode()

        payload = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
            "instance_id": instance_id
        }

        #print(payload)

        # The 'auth' parameter in requests handles basic authentication
        response = requests.post(url, data=payload)
                
        # Print the status code
        print(response.status_code)

        # Print the response content
        # print(response.json().get('access_token'))
        # Or, if you prefer to see the raw text response:
        # print(response.text)
        
        # Check the response
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            print(f"Successfully retrieved access_token:: {access_token}")
            return access_token
        else:
            print("Error:", response.status_code, response.text) 
        
    except Exception as e:
        print(f"Error making encompass auth api call: {e}")
        return ""

async def plot_the_graph(loanData: str, xAxis: str, yAxis: str):
    """
    Plot a bar chart
    
    Args:
        ctx: The context including the Supabase client
        loanData: Loan data retuned by Encompass (in JSON format)

    Returns:
        str: http request response in JSON format
    """
    try:
        print(f"plot_the_graph loandata - INPUT : {loanData}")

        # names = [loan['fields']['Loan.BorrowerName'] for loan in loanData]
        # amounts = [loan['fields']['Fields.1109'] for loan in loanData]

        names = [loan[xAxis] for loan in loanData]
        amounts = [loan[yAxis] for loan in loanData]

        # print(f"plot_the_graph loandata - names: {names}")
        # print(f"plot_the_graph loandata - amounts: {amounts}")

        # Creating the bar graph
        plt.figure(figsize=(10, 5))
        plt.barh(names, amounts, color='skyblue')
        plt.xlabel('Loan Amount ($)')
        plt.title('Loan Amounts by Borrower')
        plt.grid(axis='x')
        plt.show()
    
    except Exception as e:
        print(f"Error plotting the chart: {e}")
        return f"Error plotting the chart: {str(e)}"

async def write_text_with_filestamp(text, base_filename="output", extension="txt"):
    # Generate timestamp in format YYYYMMDD_HHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.{extension}"    
    with open(filename, "w") as file:
        file.write(text)

async def dump_json_with_filestamp(data, base_filename="output", extension="json"):
    # Generate timestamp in format YYYYMMDD_HHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%HMM%S")
    filename = f"{base_filename}_{timestamp}.{extension}"
    with open(filename, "w") as file:
        import json
        json.dump(data, file, indent=4)
    print(f"Data dumped to {filename}")

# async def main():
#     # Get URLs from Ecncompass Devconnect docs
#     token = await make_access_token_api_call()
#     print(f"GOT TOKEN - {token}")

#     # fieldnames = await make_fieldnames_api_call(token)
#     # print(f"GOT FIELD NAMES - {fieldnames}")
#     # write_text_with_filestamp(fieldnames, "encompass_fieldnames")
#     # dump_json_with_filestamp(fieldnames, "encompass_fieldnames")
#     # filter_criteria = {
#     #     "filter" : {
#     #         "canonicalName": "Loan.LastModified",
#     #         "value": "2015-05-23",
#     #         "matchType": "greaterThan",
#     #         "precision": "day"
#     #     },
#     #     "fields": [
#     #         "Fields.GUID", #guid
#     #         "Fields.364", #loan number
#     #         "Fields.1109" #loan amount
#     #     ]
#     # }
#     # filter_criteria = {
#     #     "filter":{ 
#     #         "canonicalName": "Fields.1109",
#     #         "value": "500000",
#     #         "matchType": "greaterThan"
#     #     },
#     #     "fields": [
#     #         "Fields.GUID", #guid
#     #         "Fields.364", #loan number
#     #         "Fields.1109" #loan amount
#     #     ]
#     # }
    
#     # filter_criteria = {
#     #     "filter": {
#     #         "logicalOperator": "AND",
#     #         "conditions": [
#     #             {
#     #                 "canonicalName": "Fields.1109",
#     #                 "value": "450000",
#     #                 "matchType": "greaterThan"       
#     #             },
#     #             {
#     #                 "canonicalName": "Fields.1109", 
#     #                 "value": "700000",
#     #                 "matchType": "lessThan"           
#     #             },
#     #             {
#     #                 "canonicalName": "Fields.1172",  
#     #                 "value": "Conventional",
#     #                 "matchType": "exact"                
#     #             }
#     #         ]   
#     #     },
#     #     "fields": [
#     #         "Fields.GUID",                  
#     #         "Fields.1109",                 
#     #         "Loan.BorrowerName",              
#     #         "Fields.1393",                     
#     #         "Fields.1172",
#     #         "Fields.1811",            
#     #         "Fields.2853", 
#     #         "Fields.1041", 
#     #         "Fields.CASASRN.X14"
#     #     ]
#     # }

#     # filter_criteria = {
#     #     "filter": {
#     #         "canonicalName": "Fields.1109",
#     #         "value": 450000,
#     #         "matchType": "greaterThan"       
#     #     },
#     #     "filter": {
#     #         "canonicalName": "Fields.1109", 
#     #         "value": 700000,
#     #         "matchType": "lessThan"           
#     #     },
#     #     "filter": {
#     #         "canonicalName": "Fields.1172",  
#     #         "value": "Conventional",
#     #         "matchType": "exact"                
#     #     },
#     #     "fields": [
#     #         "Fields.GUID", 
#     #         "Fields.364",                 
#     #         "Fields.1109",                 
#     #         "Loan.BorrowerName",              
#     #         "Fields.1393",                     
#     #         "Fields.1172",
#     #         "Fields.1811",            
#     #         "Fields.2853", 
#     #         "Fields.1041"
#     #     ]
#     # }
#     filter_criteria = {
#         "filter": {
#             "terms": [
#                 {
#                     "canonicalName": "Fields.1109",
#                     "value": 450000,
#                     "matchType": "greaterThan"       
#                 },
#                 {
#                     "canonicalName": "Fields.1109", 
#                     "value": 700000,
#                     "matchType": "lessThan"           
#                 },
#                 {
#                     "canonicalName": "Fields.1172",  
#                     "value": "Conventional",
#                     "matchType": "exact"                
#                 }
#             ],
#             "Operator": "And"
#         },
#         "fields": [
#             "Fields.GUID", 
#             "Fields.364",                 
#             "Fields.1109",                 
#             "Loan.BorrowerName",              
#             "Fields.1393",                     
#             "Fields.1172",
#             "Fields.1811",            
#             "Fields.2853", 
#             "Fields.1041"
#         ]
#     }
#     # result = await make_pipeline_api_call(token, filter_criteria)
    
#     # await dump_json_with_filestamp(result, "encompass_loans")

#     result = [
#         {"borrowerName":"Anderson, Jack", "loanAmount":1500000},
#         {"borrowerName":"Anderson, Jack", "loanAmount":1500000},
#         {"borrowerName":"Anderson, Jack", "loanAmount":1500000},
#         {"borrowerName":"Anderson, Jack", "loanAmount":1500000},
#         {"borrowerName":"Anderson, Jack", "loanAmount":2500000}
#     ]
#     await plot_the_graph(result, "borrowerName", "loanAmount")
#     # print(f"GOT LOANS - {result}")

# if __name__ == "__main__":
#     asyncio.run(main())

