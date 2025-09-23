# Forfatter: jsju0002
# Link til kilde:
# Beskrivelse:
## Pythonscript, der regexer create schema statements ud og replacer dem med create statements der passer til de separate miljøer.
## Output er en .sql fil der kan oprette skemaet på det rigtige miljø
# Changelog:
# ---------------------------------------------------------------
# Version | Dato       | Forfatter | Beskrivelse
# 1.0.0     04-02-2025   jsju0002    Frigivelse af kode

import sys
import re
import os.path

def check_format_and_prepare_notebook(folder, domain, notebook_filename):
    """ Takes a split notebook path and an environment letter.
    Prepares the notebook to be executed against gold_dataenheden schema in the environment
    """
    with open(os.path.join(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0],folder, domain, notebook_filename)) as notebook:
        notebook_str = notebook.read()

    # Search for valid create schema statements
    if (matches := list(re.finditer(r"CREATE *SCHEMA[ |.*\n ]*IF *NOT *EXISTS *dap_([dtp])._gold_(.*)_sandbox\.(.*)\n*;",notebook_str))):
        if len(matches) > 1:
            raise Exception('Found multiple CREATE SCHEMA IF NOT EXISTS statements.')
        else:
            match = matches[0]
    else:
        raise Exception('Did not find a CREATE SCHEMA IF NOT EXISTS statement.')

    drop_create = f"DROP SCHEMA IF EXISTS dap_d_gold_{match.group(1)}.{match.group(2)} CASCADE;\nCREATE SCHEMA IF NOT EXISTS dap_d_gold_{match.group(1)}.{match.group(2)};"
    # Add drop/create to notebook in correct place 
    notebook_str = notebook_str[0:match.span()[0]] + drop_create + notebook_str[match.span()[1]:]
    # Remove comments
    # notebook_str = re.sub(r"\/\*[\s\S]*?\*\/", "", notebook_str)

    for env in ['d','t','p']:
        with open(f'{env}_notebook.sql', 'w') as temp_notebook:
            # Remove sandbox suffix
            temp_str = re.sub(r"dap_[dtp]_gold_(.*)_sandbox", f"dap_{env}_gold_" + r"\1", notebook_str)
            # Sub env for the current env
            temp_notebook.write(re.sub(r"dap_[dtp]_", f"dap_{env}_", temp_str))

if __name__ == '__main__':
    #Split input path
    temp = sys.argv[1].split('/')
    check_format_and_prepare_notebook(temp[0], temp[1], temp[2])