import requests
import os
import json

async def make_api_call() -> str:
    try:
        # Define the API endpoint
        url = "https://api.elliemae.com/encompass/v1/loanPipeline?limit=100"
        encompass_access_token = os.getenv("ENCOMPASS_BEARER_TOKEN")

        # Set your headers (replace 'YOUR_ACCESS_TOKEN' with your actual access token)
        headers = {
            "Authorization": "Bearer {encompass_access_token}",
            "Content-Type": "application/json"
        }

        # Set the payload as needed
        payload = {
            "filter": {
                "canonicalName": "Loan.LastModified",
                "value": "2025-05-23",
                "matchType": "greaterThan",
                "precision": "day"
            }
        }

        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)

        # Check the response
        if response.status_code == 200:
            print("Success:")
            return response.json()
        else:
            print("Error:", response.status_code, response.text) 

    except Exception as e:
        print(f"Error making encompass api call: {e}")
        return ""
    

