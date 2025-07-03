# Kør denne i powershell eller command inden du kører nedenstående script
# pip install --user requests msal

import os
import requests
import msal
import json

# Hent credentials fra miljøvariabler (GitHub Actions environment)
# Sørg for at variablen i repo hedder "tenent_id" som angivet
tenant_id = os.environ.get('tenent_id')
client_id = os.environ.get('PBI_PUBLISH_SP_ID')
client_secret = os.environ.get('PBI_PUBLISH_SP_SECRET')

if not all([tenant_id, client_id, client_secret]):
    raise Exception("[ERROR] Mangler nødvendige miljøvariabler eller secrets.")

authority_url = f"https://login.microsoftonline.com/{tenant_id}"
token_url = f"{authority_url}/oauth2/v2.0/token"
scope = "https://analysis.windows.net/powerbi/api/.default"

def get_token_client_credentials():
    """Henter token via client credentials flow"""
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"[WARN] Client credentials login mislykkedes: {response.status_code} - {response.text}")
        return None

def get_token_interactive():
    """Henter token via interaktivt login (brugeren logger ind i browser)"""
    app = msal.PublicClientApplication(client_id, authority=authority_url)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent([scope], account=accounts[0])
    else:
        result = app.acquire_token_interactive(scopes=[scope])

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"[ERROR] Interaktiv login mislykkedes: {result.get('error_description')}")

# Prøv først client credentials, derefter interaktiv login
access_token = get_token_client_credentials()
if not access_token:
    print("[INFO] Falder tilbage til interaktiv login...")
    access_token = get_token_interactive()

# Brug acc
