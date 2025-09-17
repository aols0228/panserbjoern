# Forfatter: aols0228
# Link til kilde:
# 
# Beskrivelse:
# Pythonscript, der tager git diff til tidligere commit og finder ud af hvad der er sket.
# Added og Modified filer bliver håndteret for sig og Deleted files for sig.
# Outputter til GITHUB_OUTPUT filen direkte
# 
# Changelog:
# ---------------------------------------------------------------
# Version | Dato       | Forfatter | Beskrivelse
# 0.1.0     04-02-2025   jsju0002    Frigivelse af kode
# 1.0.0     25-06-2025   aols0228    Produktionsklar til dataenheden
 
import os
import re
import sys

def check_format_and_prepare_notebook(folder, domain, notebook_filename):
    """
    Takes a split notebook path and an environment letter.
    Prepares the notebook to be executed against gold_dataenheden schema in the environment.
    """
    # Simplified to just os.path.join(folder, domain, notebook_filename) for clarity and flexibility. You can revert this if your original structure requires it.
    with open(os.path.join(folder, domain, notebook_filename)) as notebook:
        notebook_str = notebook.read()


    # Search for valid CREATE SCHEMA statements (with or without backticks)
    matches = list(re.finditer(
        r"CREATE\s+SCHEMA\s+IF\s+NOT\s+EXISTS\s+`?dap_([dtp])_gold_([^`;\s]+)`?\.`?([^`;\s]+)`?\s*;",
        notebook_str,
        re.IGNORECASE
    ))
    # Regex updated:
    # - Matches dap_d/t/p_gold_<anything>.<schema_name>
    # - Supports both backticked and non-backticked identifiers
    # - Uses re.IGNORECASE for safety

    if not matches:
        raise Exception('Did not find a CREATE SCHEMA IF NOT EXISTS statement.')
    elif len(matches) > 1:
        raise Exception('Found multiple CREATE SCHEMA IF NOT EXISTS statements.')
    # Now: exactly one match
    match = matches[0]
    schema_name = match.group(3)  # schema name is now in the third capture group

    # Replace with DROP and CREATE for 'd' environment
    drop_create = (
        f"DROP SCHEMA IF EXISTS dap_d_gold_`{match.group(2)}`.`{schema_name}` CASCADE;\n"
        f"CREATE SCHEMA IF NOT EXISTS dap_d_gold_`{match.group(2)}`.`{schema_name}`;"
    )
    notebook_str = notebook_str[:match.span()[0]] + drop_create + notebook_str[match.span()[1]:]

    # Generate environment-specific versions
    # Overskriv det der allerede findes
    for env in ['t', 'p']: # vi skal ikke deploye mod d, da det er der vi udvikler
        with open(f'{env}_notebook.sql', 'w') as temp_notebook:
            # Replace dap_<env>_gold_<suffix>.<schema> accordingly
            temp_str = re.sub(r"dap_[dtp]_gold_([^`;\s]+)", f"dap_{env}_gold_\\1", notebook_str)
            temp_notebook.write(temp_str)
            grant_statement = f"GRANT SELECT ON SCHEMA dap_{env}_gold_`{match.group(2)}`.`{schema_name}` TO `AZU-B DAP-Access DataModeler`;"
            temp_notebook.write('\n' + grant_statement + '\n')

if __name__ == '__main__':
    # Example usage: python script.py folder/domain/notebook.sql
    temp = sys.argv[1].split('/')
    check_format_and_prepare_notebook(temp[0], temp[1], temp[2])
# Note: The script assumes the input path is structured as 'folder/domain/notebook.sql'.
# Ensure the script is run with the correct path structure.