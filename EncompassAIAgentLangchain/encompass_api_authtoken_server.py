# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP

import os
import requests
from dotenv import load_dotenv

load_dotenv()

mcp_authtoken=FastMCP("FetchEncompassApiAuthToken")

@mcp_authtoken.tool()
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
    

# if __name__=="__main__":
#     mcp_authtoken.run(transport="streamable-http")

if __name__ == "__main__":
    mcp_authtoken.run(
        transport="streamable-http",  # Use "http" for Streamable HTTP
        host="127.0.0.1",  # Listen on all available interfaces
        port=8002,         # Specify your desired port
        # endpoint="/mcp"    # Optional: Customize the endpoint path
    )