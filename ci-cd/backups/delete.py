import sys
import re
import os.path

def drop_schema(folder, domain, notebook_filename):
    """ Takes a split notebook path and an environment letter.
    Prepares the notebook to be executed against gold_dataenheden schema in the environment
    """
    with open(os.path.join(os.path.split(os.path.split(os.path.dirname(__file__))[0])[0],folder, domain, notebook_filename)) as notebook:
        notebook_str = notebook.read()

    # Search for valid create schema statments
    if (matches := list(re.finditer(r"CREATE *SCHEMA[ |.*\n ]*IF *NOT *EXISTS *dap_._gold_dataenheden_sandbox\.(.*)\n*;",notebook_str))):
        if len(matches) > 1:
            raise Exception('Found multiple CREATE SCHEMA IF NOT EXISTS statements.')
        else:
            match = matches[0]
    else:
        raise Exception('Did not find a CREATE SCHEMA IF NOT EXISTS statement.')

    for env in ['d', 't', 'p']:
        drop = notebook_str[0:match.span()[0]]+ f"DROP SCHEMA IF EXISTS dap_{env}_gold_dataenheden.{match.group(1)} CASCADE;"

        with open(f'{env}_notebook.sql', 'w') as temp_notebook:
            temp_notebook.write(drop)

if __name__ == '__main__':
    #Split input path
    temp = sys.argv[1].split('/')
    drop_schema(temp[0], temp[1], temp[2])
