import requests
import http.client
import json

# Udfyld disse med dine egne værdier
tenant_id = 'your-tenant-id'
client_id = 'your-client-id'
client_secret = 'your-client-secret'
resource = 'https://analysis.windows.net/powerbi/api'  # Power BI resource
authority = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'

# Hent access token
token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'resource': resource
}
token_response = requests.post(authority, data=token_data)
token_json = token_response.json()

if 'access_token' not in token_json:
    raise Exception(f"[ERROR] Kunne ikke hente token: {token_json}")

access_token = token_json['access_token']

# Kald Power BI API
conn = http.client.HTTPSConnection("api.powerbi.com")
headers = {
    'Authorization': f'Bearer {access_token}'
}
conn.request("GET", "/v1.0/myorg/groups", '', headers)
res = conn.getresponse()
data = res.read()

try:
    workspaces = json.loads(data.decode('utf-8'))
except json.JSONDecodeError as e:
    raise Exception(f"[ERROR] Kunne ikke parse JSON fra API: {e}")

workspace_id = next((ws['id'] for ws in workspaces['value'] if ws['name'] == 'Sandbox_DAP'), None)
if not workspace_id:
    raise Exception("[ERROR] Workspace ID er ikke angivet eller fundet.")

print(f"Workspace ID: {workspace_id}")
