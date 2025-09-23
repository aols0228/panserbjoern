# Forfatter: aols0228
# Link til kilde:
#
# Beskrivelse:
# Pythonscript, der finder ID'et på en model der er deployet til et PowerBI workspace. Hvis det findes, bliver det slettet
# Bemærk: Dette script kræver kun modelnavnet (ikke stien til database.json), 
# da det bruger Power BI API til at finde og slette datasættet baseret på navnet.
# 
# Changelog:
# ---------------------------------------------------------------
# Version | Dato       | Forfatter | Beskrivelse
# 0.1.0     04-02-2025   jsju0002    Oprettelse af kode
# 0.2.0     05-06-2025   aols0228    Tilføjet håndtering af model name fra database.json og fleksibilitet vil at vælge mellem model name og folder name, når der deployes
# 1.0.0     25-06-2025   aols0228    Produktionsklar til dataenheden - model_delete.py virker dog ikke endnu

import http.client
import json
import os
import sys

# Hent modelnavn og adgangstoken fra argumenter
model_name = sys.argv[1].strip()
access_token = sys.argv[2].strip()
workspace_id = os.getenv('FABRIC_WORKSPACE_ID', '').strip()
entra_token = os.getenv('ENTRA_TOKEN', '').strip()

print(f"[INFO] Starter sletning af model: '{model_name}'")

# Setup forbindelse til Power BI API
conn = http.client.HTTPSConnection("api.powerbi.com")
headers = {
    'Authorization': f'Bearer {access_token}'
}
payload = ''


if not workspace_id:
    raise Exception("[ERROR] Fabric Workspace ID er ikke angivet eller fundet.")
print(f"[INFO] Bruger workspace ID: {workspace_id}")

# Hent alle datasæt i workspace
print("[INFO] Henter datasæt fra Fabric Workspace...")
conn.request("GET", f"/v1.0/myorg/groups/{workspace_id}/datasets", payload, headers)
res1 = conn.getresponse()
data = res1.read()

try:
    datasets = json.loads(data.decode('utf-8'))
except json.JSONDecodeError as e:
    raise Exception(f"[ERROR] Kunne ikke parse JSON fra API: {e}")

# Søg efter datasæt med det ønskede navn
found = False
for dataset in datasets.get("value", []):
    dataset_name = dataset["name"].strip()
    if dataset_name == model_name:
        dataset_id = dataset["id"]
        print(f"[INFO] Model fundet: '{dataset_name}' (ID: {dataset_id}) - forsøger at slette...")

        # Forsøg at slette datasættet
        conn.request("DELETE", f"/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}", payload, headers)
        res2 = conn.getresponse()

        if res2.getcode() == 200:
            print(f"[SUCCESS] Model slettet: '{model_name}'")
        else:
            error_msg = res2.read().decode('utf-8')
            raise Exception(f"[ERROR] Model fundet i workspace, men kunne ikke slettes: {res2.getcode()} {error_msg}")
        found = True
        break

if not found:
    raise Exception(f"[ERROR] Model ikke fundet i workspace: '{model_name}'")
# Afslut forbindelse
conn.close()