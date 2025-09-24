#!/usr/bin/env python3
import os
import re
import sys

def get_required_env_vars():
    """Henter og validerer alle nødvendige environment variables."""
    env_vars = {}
    
    target_env_prefix = os.getenv('target_environment_prefix', '').strip()
    if not target_env_prefix:
        print("[ERROR] target_environment_prefix environment variable er ikke angivet.")
        sys.exit(1)
    env_vars['target_environment_prefix'] = target_env_prefix
    
    return env_vars

if __name__ == '__main__':
    # Hent environment variables
    env_vars = get_required_env_vars()
    
    # Parse path: folder/domain/notebook.sql
    temp = sys.argv[1].split('/')
    notebook_path = os.path.join(temp[0], temp[1], temp[2])
    
    # Læs notebook
    with open(notebook_path) as notebook:
        notebook_content = notebook.read()
    
    # Get target environment
    env = env_vars['target_environment_prefix']
    
    # Replace environment references
    env_content = re.sub(r"dap_[dtp]_gold_([^`;\s]+)", f"dap_{env}_gold_\\1", notebook_content)
    
    # Write output file
    with open(f'{env}_notebook.sql', 'w') as temp_notebook:
        temp_notebook.write(env_content)
    
    print(f"[INFO] Notebook genereret for {env} environment")