# model-api
# Forfatter: aols0228
# Link til kilde:
#
# Beskrivelse:
# Unified PowerBI model API script til delete, refresh og andre model operationer.
# Bruger environment variables for alle inputs og MODEL_OPERATION for at bestemme operation.
# Usage: Sæt MODEL_OPERATION environment variable til "delete", "refresh" etc.
# 
# Changelog:
# ---------------------------------------------------------------
# Version | Dato       | Forfatter | Beskrivelse
# 1.0.0     22-09-2025   aols0228    Unified API script - eliminerer code duplication mellem delete/refresh scripts
# 1.1.0     22-09-2025   aols0228    Tilføjet validate_refresh_model() operation med intelligent loop og token expiration detection
# 1.2.0     22-09-2025   aols0228    Refaktoreret environment variable handling - elimineret code duplication, omdøbt til get_env_vars()
# 1.3.0     22-09-2025   aols0228    Integreret hjælpefunktioner i hovedfunktioner, tilføjet struktur kommentarer

import http.client
import json
import os
import sys
import time

# =============================================================================
# CONFIGURATION & UTILITIES
# =============================================================================

# Platform-compatible UTF-8 encoding setup
try:
    # Python 3.7+ har reconfigure metoden
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    # Fallback hvis reconfigure fejler - ikke kritisk
    pass

def get_env_vars():
    """Henter og validerer alle nødvendige environment variables."""
    env_vars = {
        'workspace': os.getenv('FABRIC_WORKSPACE', '').strip(),
        'entra_token': os.getenv('ENTRA_TOKEN', '').strip(),
        'workspace_id': os.getenv('FABRIC_WORKSPACE_ID', '').strip(),
        'model_name': os.getenv('MODEL_NAME', '').strip(),
        'operation': os.getenv('MODEL_OPERATION', '').strip().lower()
    }
    
    # Valider at alle værdier er til stede
    missing = [k.upper() for k, v in env_vars.items() if not v]
    if missing:
        for var in missing:
            print(f"[ERROR] {var} environment variable er ikke angivet.")
        print(f"[INFO] MODEL_OPERATION skal være: delete, refresh, validate_refresh")
        sys.exit(1)
    
    # Valider operation
    valid_operations = ['delete', 'refresh', 'validate_refresh']
    if env_vars['operation'] not in valid_operations:
        print(f"[ERROR] Ugyldig MODEL_OPERATION: '{env_vars['operation']}'")
        print(f"[INFO] Gyldige operationer: {', '.join(valid_operations)}")
        sys.exit(1)
    
    return env_vars

def call_powerbi_api(method, endpoint):
    """
    Generic Power BI REST API wrapper med token expiration detection.
    
    Args:
        method: HTTP method (GET, POST, DELETE)
        endpoint: API endpoint URL path
        
    Returns:
        tuple: (success, data/error_message)
    """
    entra_token = os.getenv('ENTRA_TOKEN', '').strip()
    conn = http.client.HTTPSConnection("api.powerbi.com")
    headers = {'Authorization': f"Bearer {entra_token}"}
    
    try:
        conn.request(method, endpoint, '', headers)
        response = conn.getresponse()
        data = response.read()
        
        if method == "GET":
            if response.getcode() == 200:
                try:
                    return True, json.loads(data.decode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Kunne ikke parse JSON fra API: {e}")
                    print(f"[DEBUG] Response: {data.decode('utf-8')[:500]}")
                    return False, f"JSON parse error: {e}"
            elif response.getcode() == 401:
                return False, "TOKEN_EXPIRED"
            else:
                return False, f"HTTP {response.getcode()}: {data.decode('utf-8')}"
        
        elif method == "DELETE":
            if response.getcode() == 200:
                return True, "Success"
            elif response.getcode() == 401:
                return False, "TOKEN_EXPIRED"
            else:
                return False, f"HTTP {response.getcode()}: {data.decode('utf-8')}"
        
        elif method == "POST":
            # For refresh operationer forventer vi HTTP 202 (Accepted)
            if response.getcode() == 202:
                return True, "Success"
            elif response.getcode() == 401:
                return False, "TOKEN_EXPIRED"
            else:
                return False, f"HTTP {response.getcode()}: {data.decode('utf-8')}"
        
        else:
            return False, f"Unsupported HTTP method: {method}"
            
    except Exception as e:
        return False, f"API call failed: {e}"
    finally:
        conn.close()

def find_dataset_by_name(model_name, workspace_id):
    """
    Hjælpefunktion: Finder dataset ID baseret på model navn ved at søge i workspace.
    Genbruges af alle tre hovedoperationer.
    
    Args:
        model_name: Navn på model at finde
        workspace_id: Workspace ID
        
    Returns:
        str: Dataset ID eller None hvis ikke fundet
    """
    # Hent alle datasæt i workspace
    endpoint = f"/v1.0/myorg/groups/{workspace_id}/datasets"
    success, response = call_powerbi_api("GET", endpoint)
    
    if not success:
        if response == "TOKEN_EXPIRED":
            print(f"[ERROR] Entra token udløbet under hentning af datasæt")
            print(f"[INFO] Regenerer token i GitHub Actions og prøv igen")
        else:
            print(f"[ERROR] Kunne ikke hente datasæt: {response}")
        return None
    
    datasets = response.get("value", [])
    
    # Søg efter dataset med det ønskede navn
    for dataset in datasets:
        if dataset["name"].strip() == model_name:
            return dataset["id"]
    
    return None

# =============================================================================
# HOVEDOPERATIONER - BUSINESS LOGIC
# =============================================================================

def delete_model():
    """
    HOVEDOPERATION: Sletter en Power BI model fra workspace.
    
    Flow:
    1. Find dataset ID baseret på model navn
    2. Kald DELETE API endpoint
    3. Håndter resultat og token expiration
    
    Returns:
        bool: True hvis success, False hvis fejl
    """
    env = get_env_vars()
    
    print(f"[INFO] Starter sletning af '{env['model_name']}' fra workspace '{env['workspace']}'")
    print(f"[INFO] Bruger workspace ID: {env['workspace_id']}")
    
    # Find dataset ID
    print(f"[INFO] Søger efter model '{env['model_name']}' i workspace...")
    dataset_id = find_dataset_by_name(env['model_name'], env['workspace_id'])
    
    if not dataset_id:
        print(f"[INFO] Model '{env['model_name']}' ikke fundet i workspace '{env['workspace']}' - ingen handling nødvendig")
        return True
    
    # Slet datasættet via REST API
    print(f"[INFO] Model '{env['model_name']}' fundet (ID: {dataset_id}) - forsøger at slette...")
    endpoint = f"/v1.0/myorg/groups/{env['workspace_id']}/datasets/{dataset_id}"
    success, error_msg = call_powerbi_api("DELETE", endpoint)
    
    if success:
        print(f"[SUCCESS] Model '{env['model_name']}' slettet fra workspace '{env['workspace']}'")
        return True
    elif error_msg == "TOKEN_EXPIRED":
        print(f"[ERROR] Entra token udløbet under sletning af model '{env['model_name']}'")
        print(f"[INFO] Regenerer token i GitHub Actions og prøv igen")
        return False
    else:
        print(f"[ERROR] Model '{env['model_name']}' kunne ikke slettes: {error_msg}")
        return False

def refresh_model():
    """
    HOVEDOPERATION: Starter refresh af en Power BI model i workspace.
    
    Flow:
    1. Find dataset ID baseret på model navn
    2. Kald POST refresh API endpoint (asynkron operation)
    3. Håndter resultat og token expiration
    
    Note: Dette starter kun refresh'en - brug validate_refresh_model() for at vente på completion.
    
    Returns:
        bool: True hvis refresh startet, False hvis fejl
    """
    env = get_env_vars()
    
    print(f"[INFO] Starter refresh af '{env['model_name']}' i workspace '{env['workspace']}'")
    print(f"[INFO] Bruger workspace ID: {env['workspace_id']}")
    
    # Find dataset ID
    print(f"[INFO] Søger efter model '{env['model_name']}' i workspace...")
    dataset_id = find_dataset_by_name(env['model_name'], env['workspace_id'])
    
    if not dataset_id:
        print(f"[ERROR] Model '{env['model_name']}' ikke fundet i workspace '{env['workspace']}'")
        return False
    
    # Start refresh via REST API (asynkron operation)
    print(f"[INFO] Model '{env['model_name']}' fundet (ID: {dataset_id}) - forsøger at refreshe...")
    endpoint = f"/v1.0/myorg/groups/{env['workspace_id']}/datasets/{dataset_id}/refreshes"
    success, error_msg = call_powerbi_api("POST", endpoint)
    
    if success:
        print(f"[SUCCESS] Model '{env['model_name']}' refresh startet i workspace '{env['workspace']}'")
        return True
    elif error_msg == "TOKEN_EXPIRED":
        print(f"[ERROR] Entra token udløbet under refresh af model '{env['model_name']}'")
        print(f"[INFO] Regenerer token i GitHub Actions og prøv igen")
        return False
    else:
        print(f"[ERROR] Model '{env['model_name']}' kunne ikke refreshes: {error_msg}")
        return False

def validate_refresh_model():
    """
    HOVEDOPERATION: Validerer og venter på at en Power BI model refresh completion.
    
    Flow:
    1. Find dataset ID baseret på model navn
    2. Poll refresh history API i loop med intelligente intervaller
    3. Håndter forskellige refresh statuses (InProgress, Completed, Failed)
    4. Stop ved token expiration eller timeout
    
    Loop logik:
    - Venter 30 sekunder mellem checks
    - Maximum 10 minutter total ventetid (for at undgå token expiration)
    - Stopper kun ved "InProgress" - alle andre statuses stopper med det samme
    
    Returns:
        bool: True hvis refresh completed successfully, False hvis fejl/timeout
    """
    env = get_env_vars()
    
    print(f"[INFO] Validerer seneste refresh status for '{env['model_name']}' i workspace '{env['workspace']}'")
    print(f"[INFO] Bruger workspace ID: {env['workspace_id']}")
    
    # Find dataset ID
    print(f"[INFO] Søger efter model '{env['model_name']}' i workspace...")
    dataset_id = find_dataset_by_name(env['model_name'], env['workspace_id'])
    
    if not dataset_id:
        print(f"[ERROR] Model '{env['model_name']}' ikke fundet i workspace '{env['workspace']}'")
        return False
    
    print(f"[INFO] Model '{env['model_name']}' fundet (ID: {dataset_id}) - validerer refresh status...")
    
    # Intelligent polling loop configuration
    max_wait_minutes = 10  # Balanceret timeout for at undgå token expiration
    wait_seconds = 30      # Kortere interval for hurtigere feedback
    attempts = 0
    max_attempts = (max_wait_minutes * 60) // wait_seconds
    
    while attempts < max_attempts:
        attempts += 1
        
        # Hent refresh historie via REST API
        refresh_endpoint = f"/v1.0/myorg/groups/{env['workspace_id']}/datasets/{dataset_id}/refreshes"
        success, response = call_powerbi_api("GET", refresh_endpoint)
        
        if not success:
            if response == "TOKEN_EXPIRED":
                elapsed_minutes = (attempts * wait_seconds) // 60
                print(f"[ERROR] Entra token udløbet efter {elapsed_minutes} minutter")
                print(f"[INFO] Regenerer token i GitHub Actions og prøv igen")
                return False
            else:
                print(f"[ERROR] Kunne ikke hente refresh historie: {response}")
                return False
        
        # Parse refresh historie
        refreshes = response.get("value", [])
        if not refreshes:
            print(f"[INFO] Ingen refresh historie fundet for model '{env['model_name']}'")
            return True  # Ikke en fejl hvis der ikke er refresh historie
        
        # Den første refresh er den seneste (sorteret efter start time descending)
        latest_refresh = refreshes[0]
        status = latest_refresh.get("status", "Unknown")
        start_time = latest_refresh.get("startTime", "N/A")
        end_time = latest_refresh.get("endTime", "N/A")
        
        if attempts == 1:  # Vis detaljer første gang
            print(f"[INFO] Seneste refresh:")
            print(f"[INFO]   Status: {status}")
            print(f"[INFO]   Start tid: {start_time}")
            if end_time != "N/A":
                print(f"[INFO]   Slut tid: {end_time}")
        
        # Håndter forskellige refresh statuses
        if status == "Completed":
            print(f"[SUCCESS] Model '{env['model_name']}' refresh gennemført successfully efter {attempts} attempts")
            return True
        elif status == "Failed":
            # Vis fejl detaljer hvis tilgængelige
            if "serviceExceptionJson" in latest_refresh:
                error_details = latest_refresh["serviceExceptionJson"]
                print(f"[ERROR] Model '{env['model_name']}' refresh fejlede: {error_details}")
            else:
                print(f"[ERROR] Model '{env['model_name']}' refresh fejlede")
            return False
        elif status == "InProgress":
            # Kun hvis InProgress fortsætter vi med at vente
            elapsed_minutes = (attempts * wait_seconds) // 60
            remaining_minutes = max_wait_minutes - elapsed_minutes
            print(f"[INFO] Refresh er stadig i gang... (venter {wait_seconds}s, {remaining_minutes} min tilbage, attempt {attempts}/{max_attempts})")
            
            if attempts < max_attempts:
                time.sleep(wait_seconds)
                continue  # Fortsæt loop
            else:
                print(f"[WARNING] Timeout efter {max_wait_minutes} minutter - refresh er stadig i gang")
                return False
        else:
            # Al andre statuses stopper loop'et med det samme
            print(f"[ERROR] Model '{env['model_name']}' seneste refresh har uventet status: {status}")
            return False
    
    # Dette skulle aldrig nås grundet loop logik, men for sikkerhedens skyld
    print(f"[ERROR] Maksimalt antal forsøg ({max_attempts}) nået")
    return False

# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

def main():
    """
    Hovedorkestrering: Router til den korrekte operation baseret på MODEL_OPERATION env var.
    
    Supported operations:
    - delete: Slet model fra workspace
    - refresh: Start model refresh (asynkront)
    - validate_refresh: Valider og vent på refresh completion
    """
    try:
        env = get_env_vars()
        operation = env['operation']
        
        if operation == 'delete':
            success = delete_model()
        elif operation == 'refresh':
            success = refresh_model()
        elif operation == 'validate_refresh':
            success = validate_refresh_model()
        else:
            print(f"[ERROR] Ukendt operation: {operation}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Uventet fejl: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()