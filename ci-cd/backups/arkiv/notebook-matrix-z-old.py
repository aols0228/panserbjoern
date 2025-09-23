# Forfatter: jsju0002
# Link til kilde:
# Beskrivelse:
## Pythonscript, der tager git diff til tidligere commit og finder ud af hvad der er sket.
## Added og Modified filer bliver håndteret for sig og Deleted files for sig.
## Outputter til GITHUB_OUTPUT filen direkte
# Changelog:
# ---------------------------------------------------------------
# Version | Dato       | Forfatter | Beskrivelse
# 1.0.0     04-02-2025   jsju0002    Frigivelse af kode

import sys
import os

def set_output(name, value):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'{name}={value}', file=fh)

temp = sys.argv[1]
# temp = """M	.github/workflows/filefilter_gitdiff.yml
# M	Notebook/SPAnvendelse_M1/SPAnvendelse_M1.sql"""

added_modified = []
deleted = []

for i in temp.split('\n'):
    if len(i.split('\t')) == 2:
        status = i.split('\t')[0]
        name   = i.split('\t')[1]
        # print(status, name)

    if name.startswith("Notebook"):
        if status in ["A", "M"]:
            added_modified.append(name)
        elif status in ["D"]:
            deleted.append(name)
        else:
            raise Exception(f"Unhandles status: {status}")

set_output("changed_notebooks", added_modified)
set_output("deleted_notebooks", deleted)