import sys, os

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

