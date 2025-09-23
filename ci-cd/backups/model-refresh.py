# model-refresh
# Forfatter: aols0228
# Link til kilde:
#
# Beskrivelse:
# Pythonscript, der finder ID'et på en model der er deployet til et PowerBI workspace. Hvis det findes, bliver det refreshed
# Bemærk: Dette script bruger environment variables for alle inputs og Power BI API til at finde og refreshe datasættet baseret på navnet.
# 
# Changelog:
# ---------------------------------------------------------------
# Version | Dato       | Forfatter | Beskrivelse
# 0.1.0     04-02-2025   jsju0002    Oprettelse af kode
# 0.2.0     05-06-2025   aols0228    Tilføjet håndtering af model name fra database.json og fleksibilitet vil at vælge mellem model name og folder name, når der deployes
# 1.0.0     25-06-2025   aols0228    Produktionsklar til dataenheden - model_delete.py virker dog ikke endnu
# 1.1.0     16-09-2025   jsju0002    Modificeret til at refreshe istedet for at slette
# 1.2.0     22-09-2025   aols0228    Opdateret til konsistent brug af environment variables i stedet for sys.argv
# 1.3.0     22-09-2025   aols0228    Komplet refaktorering: fjernet sys.argv afhængighed, tilføjet strukturerede funktioner (call_api), 
#                                    korrekt HTTP 202 håndtering for refresh operationer, og gjort konsistent med model-delete.py

import http.client
import json
import os
import sys

def get_required_env_vars():
    """Henter og validerer alle nødvendige environment variables."""
    env_vars = {
        'entra_token': os.getenv('ENTRA_TOKEN', '').strip(),
        'workspace': os.getenv('FABRIC_WORKSPACE', '').strip(),
        'workspace_id': os.getenv('FABRIC_WORKSPACE_ID', '').strip(),
        'model_name': os.getenv('MODEL_NAME', '').strip()
    }
    
    # Valider at alle værdier er til stede
    missing = [k.upper() for k, v in env_vars.items() if not v]
    if missing:
        for var in missing:
            print(f"[ERROR] {var} environment variable er ikke angivet.")
        sys.exit(1)
    
    return env_vars

def call_api(method, dataset_id, entra_token, workspace_id):
    """
    Kalder Power BI API for dataset operationer i et workspace.
    
    Args:
        method: HTTP method (GET for list, POST for refresh)
        dataset_id: Dataset ID for POST, None for GET all
        entra_token: Entra ID bearer token til authentication
        workspace_id: Workspace ID
    """
    # Etabler API forbindelse
    conn = http.client.HTTPSConnection("api.powerbi.com")
    headers = {'Authorization': f"Bearer {entra_token}"}
    
    # Byg endpoint URL baseret på operation
    base_url = f"/v1.0/myorg/groups/{workspace_id}/datasets"
    if dataset_id:
        endpoint = f"{base_url}/{dataset_id}/refreshes"  # POST refresh specific dataset
    else:
        endpoint = base_url  # GET all datasets
    
    try:
        conn.request(method, endpoint, '', headers)
        response = conn.getresponse()
        data = response.read()
        
        if method == "GET" and response.getcode() == 200:
            try:
                return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"[ERROR] Kunne ikke parse JSON fra API: {e}")
                print(f"[DEBUG] Response: {data.decode('utf-8')[:500]}")
                sys.exit(1)
        elif method == "POST":
            return response.getcode() == 202, data.decode('utf-8')  # 202 Accepted for refresh
        else:
            print(f"[ERROR] API kald fejlede. HTTP {response.getcode()}: {data.decode('utf-8')}")
            return None
    finally:
        conn.close()

def refresh_model():
    """Hovedfunktion der refresher en model i Power BI workspace."""
    
    # Hent environment variables
    env = get_required_env_vars()
    
    print(f"[INFO] Starter refresh af '{env['model_name']}' i workspace '{env['workspace']}'")
    print(f"[INFO] Bruger workspace ID: {env['workspace_id']}")
    
    try:
        # Hent alle datasæt i workspace
        print(f"[INFO] Henter datasæt fra workspace '{env['workspace']}'...")
        datasets = call_api(
            "GET", 
            None,  # Ingen dataset_id for GET all
            env['entra_token'],
            env['workspace_id']
        )
        
        if not datasets:
            print(f"[ERROR] Kunne ikke hente datasæt fra workspace")
            sys.exit(1)
        
        # Søg efter datasæt med det ønskede navn
        dataset_id = None
        for dataset in datasets.get("value", []):
            if dataset["name"].strip() == env['model_name']:
                dataset_id = dataset["id"]
                break
        
        if not dataset_id:
            print(f"[ERROR] Model '{env['model_name']}' ikke fundet i workspace '{env['workspace']}'")
            sys.exit(1)
        
        # Refresh datasættet
        print(f"[INFO] Model '{env['model_name']}' fundet (ID: {dataset_id}) - forsøger at refreshe...")
        success, error_msg = call_api(
            "POST",
            dataset_id,  # Specifik dataset ID
            env['entra_token'],
            env['workspace_id']
        )
        
        if success:
            print(f"[SUCCESS] Model '{env['model_name']}' refresh startet i workspace '{env['workspace']}'")
        else:
            print(f"[ERROR] Model '{env['model_name']}' kunne ikke refreshes: {error_msg}")
            sys.exit(1)
            
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Uventet fejl: {e}")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    refresh_model()