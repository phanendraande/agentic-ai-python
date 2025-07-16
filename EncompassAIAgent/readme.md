python -m venv venv
.\venv\scripts\activate (OR) source ./venv/bin/activate 
playwright install
pip install -r .\requirements.txt
streamlit run streamlit_ui.py



filter_json = {
        "filter": {
            "canonicalName": "Fields.1109",
            "value": "500000",
            "matchType": "greaterThan"
        },
        "fields": [
            "Fields.GUID", #guid
            "Fields.364", #loan number
            "Fields.1109" #loan amount
            "Loan.BorrowerName",
            "Fields.1393", #loan status
            "Fields.1172", #loan type (conventional, fha, usda, va, other) 
            "Fields.1811", #Occupancy (P/S/I)
            "Fields.67", #Borr Experian Fico
            "Fields.2849",#Borr Actual Fico Score
            "Fields.4177", #Co-Borr Credit Score for Decision Making
            "Fields.HMDA.X116#2", #Borr Credit Score for Decision Making - 2nd
            "Fields.2853", #Lock Request Credit Score for Decision Making
            "Fields.1041", #Subject Property Type (Fannie Mae) - attached / detached / condominium / High-raise / manufactured etc
            "Fields.CASASRN.X14", #Freddie Mac Lender Property Type - single family / multi family / manufactured / high-raise etc
            "Fields.16", #Subject Property # Units
        ]
    }

filter_criteria = {
        "filter": {
            "terms": [
                {
                    "canonicalName": "Fields.1109",
                    "value": 450000,
                    "matchType": "greaterThan"       
                },
                {
                    "canonicalName": "Fields.1109", 
                    "value": 700000,
                    "matchType": "lessThan"           
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
            "Fields.364",                 
            "Fields.1109",                 
            "Loan.BorrowerName",              
            "Fields.1393",                     
            "Fields.1172",
            "Fields.1811",            
            "Fields.2853", 
            "Fields.1041"
        ]
    }

# payload = {
        #     "filter": {
        #         "canonicalName": "Loan.Amount",
        #         "value": 500000,
        #         "matchType": "greaterThan"
        #     },
        #     "fields": [
        #         "Loan.ID",
        #         "Loan.Amount"
        #     ]
        # }
        # # Set the payload as needed
        # payload = {
        #     "filter": {
        #         "canonicalName": "Loan.LastModified",
        #         "value": "2025-05-23",
        #         "matchType": "greaterThan",
        #         "precision": "day"
        #     }
        # }

        

    "Show me loans with loan amounts over 500000",
    "Find active conventional loans for single family homes",
    "Get all FHA loans with credit scores above 650 from the last 6 months",
    "Show me investment property loans between $300k and $800k"
 