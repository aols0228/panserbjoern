# Forfatter: jsju0002
# Link til kilde:
# Beskrivelse:
## Pythonscript, der finder ID'et på en model der er deployet til et PowerBI workspace. Hvis det findes, bliver det slettet
# Changelog:
# ---------------------------------------------------------------
# Version | Dato       | Forfatter | Beskrivelse
# 1.0.0     04-02-2025   jsju0002    Frigivelse af kode

import http.client
import json
import sys

# Setup connection
conn = http.client.HTTPSConnection("api.powerbi.com")
payload = ''
headers = {
  'Authorization': f'Bearer {sys.argv[2]}'
}

# Hvis du ændrer her, skal du også ændre i model_deploy.yml
# Model_Prod group id:
# workspace_id = "624142ec-9003-4532-8b7a-049ece240328"

# Sandbox_DAP group id:
# workspace_id = "ddcf72c9-95e5-4f5f-a69d-334cae22b09e"

# DAP_P_Model_Cøk_Dataenheden group id:
workspace_id = "f0b1c8d2-3a4e-4b5c-8d6e-7f8a9b0c1d2e"

# Get all datasets in workspace
conn.request("GET", f"/v1.0/myorg/groups/{workspace_id}/datasets", payload, headers)
res1 = conn.getresponse()

data = res1.read()
dct = json.loads(data.decode('utf-8'))

# Check each dataset if its the correct dataset name
for dataset in dct["value"]:
    if dataset["name"] == sys.argv[1]:
        # Try to delete dataset
        conn.request("DELETE", f"/v1.0/myorg/groups/{workspace_id}/datasets/{dataset['id']}", payload, headers)
        res2 = conn.getresponse()
        
        if res2.getcode() == 200:
            print(f"Model deleted: {sys.argv[1]}")
            break
        else:
            raise Exception(f"Model found but not deleted: {res2.getcode()} {json.loads(res2.read().decode('utf-8'))}")
else:
    raise Exception(f"Model not found: {sys.argv[1]}")
