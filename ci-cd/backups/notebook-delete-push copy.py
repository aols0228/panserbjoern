# Forfatter: aols0228
# Link til kilde:
# 
# Beskrivelse:
# Pythonscript, der regexer CREATE SCHEMA statements ud og genererer .sql-filer, der dropper skemaet i forskellige miljøer.
# 
# Changelog:
# ---------------------------------------------------------------
# Version | Dato       | Forfatter | Beskrivelse
# 0.1.0   | 04-02-2025 | jsju0002  | Oprettelse af kode
# 0.2.0   | 31-05-2025 | jsju0002  | Opdateret regex og fjernet CREATE-logik. Fokus kun på DROP.
# 1.0.0   | 25-06-2025 | aols0228  | Produktionsklar til dataenheden
# 1.1.0   | 30-07-2025 | aols0228  | Fjernet hardkodning af "dataenheden", gjort regex mere fleksibel

import os
import re
import sys

def drop_schema(folder, domain, notebook_filename):
    """
    Læser en SQL-notebook, identificerer CREATE SCHEMA IF NOT EXISTS-statementet,
    og genererer .sql-filer, der dropper skemaet for hvert miljø.
    """

    # Sammensætter den fulde sti til notebook-filen
    path = os.path.join(folder, domain, notebook_filename)
    with open(path) as notebook:
        notebook_str = notebook.read()

    # Matcher CREATE SCHEMA IF NOT EXISTS med eller uden backticks
    # Regex'en fanger miljø (d/t/p), domæne og skemanavn
    matches = list(re.finditer(
        # r"CREATE\s+SCHEMA\s+IF\s+NOT\s+EXISTS\s+`?dap_([dtp])_gold_([^`._]+)`?\.`?([^`;\s]+)`?\s*;",
        # Rettet potentiel fejl: [^`._]+ ekskluderer underscores, så fx "sys_administration" matches ikke
        # Rettet til [^`.]+ så underscores er tilladt
        r"CREATE\s+SCHEMA\s+IF\s+NOT\s+EXISTS\s+`?dap_([dtp])_gold_([^`.]+)`?\.`?([^`;\s]+)`?\s*;",
        notebook_str,
        re.IGNORECASE
    ))

    if not matches:
        raise Exception('Did not find a CREATE SCHEMA IF NOT EXISTS statement.')
    elif len(matches) > 1:
        raise Exception('Found multiple CREATE SCHEMA IF NOT EXISTS statements.')

    match = matches[0]
    facility = match.group(2)
    schema = match.group(3)

    # Genererer DROP SCHEMA statements for hvert miljø
    for env in ['t', 'p']:
        drop_statement = f"DROP SCHEMA IF EXISTS `dap_{env}_gold_{facility}`.`{schema}` CASCADE;"
        
        # Skriver DROP-statementet til en separat .sql-fil for hvert miljø
        # vi dropper det hele, så vi skal ikke lave temp_str som i deploy-scriptet
        with open(f'{env}_notebook.sql', 'w') as temp_notebook:
            temp_notebook.write(drop_statement)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        script_name = os.path.basename(sys.argv[0])
        print(f"Usage: python {script_name} folder/domain/notebook.sql")
        sys.exit(1)

    temp = sys.argv[1].split('/')
    drop_schema(temp[0], temp[1], temp[2])
