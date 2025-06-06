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

import os
import sys

# Funktion til at skrive output til GitHub Actions outputfil
def set_output(name, value):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'{name}={value}', file=fh)

# Input fra kommandolinjen – forventes at være output fra `git diff --name-status`
temp = sys.argv[1]

models_to_deploy = []
models_to_delete = []

# Gennemgår hver linje i inputtet
for i in temp.split('\n'):
    if len(i.split('\t')) == 2:
        status = i.split('\t')[0]  # A (Added), M (Modified), D (Deleted)
        name   = i.split('\t')[1]  # Filnavn/sti
        print(status, name)

    # Filtrerer kun JSON-filer i "Model"-mapper
    if name.startswith("Model") and name.endswith(".json"):
        if status == "D":
            if name.endswith("database.json"):
                    # Hvis database.json slettes, skal modellen slettes
                    # Vi antager, at database.json indeholder modelnavnet 
                models_to_delete.append(name)
            else:
                # Andre slettede JSON-filer betragtes som modeller, der skal deployes
                models_to_deploy.append(name)
        elif status in ["A", "M"]:
            # Tilføjede eller ændrede filer skal deployes
            models_to_deploy.append(name)
        else:
            raise Exception(f"Unhandles status: {status}")

unique_models_to_deploy = list()
unique_models_to_delete = list()
already_added = list()

# Udtrækker domæne og modelnavn fra sti og sikrer unikke modeller til sletning
for model in models_to_delete:
    domain, name = model.split('/')[1], model.split('/')[2]  # <-- Her læses navnet fra mappen
    if name not in already_added:
        unique_models_to_delete.append({"domain": domain, "name": name})
        already_added.append(name)

# Udtrækker domæne og modelnavn fra sti og sikrer unikke modeller til deployment
for model in models_to_deploy:
    domain, name = model.split('/')[1], model.split('/')[2]  # <-- Her bruges navnet til deployment
    if name not in already_added:
        unique_models_to_deploy.append({"domain": domain, "name": name})
        already_added.append(name)

# Skriver resultaterne til GitHub Actions output
set_output("models_to_deploy", list(unique_models_to_deploy))
set_output("models_to_delete", list(unique_models_to_delete))
