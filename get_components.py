# get_components.py
# -----------------
# Get AXES-LITE components and store paths - see README.md for details

import os
import subprocess
import json
import pprint
from scaffoldutils import utils

# clone components

# TODO: should download a specific tag

if not os.path.isdir('cpuvisor-srv'):
    subprocess.call('git clone git@github.com:kencoken/cpuvisor-srv.git', shell=True)
    with utils.change_cwd('cpuvisor-srv'):
        subprocess.call('git checkout al-integration-prep', shell=True) # TODO: remove this custom branch

if not os.path.isdir('limas'):
    subprocess.call('hg clone ssh://hg@bitbucket.org/alyr/limas', shell=True)

if not os.path.isdir('axes-home'):
    subprocess.call('git clone git@bitbucket.org:kevinmcguinness/axes-home.git', shell=True)

# update component_paths.json with paths if is default value

default_val = '<PATH>'
paths = {
    'cpuvisor-srv': 'cpuvisor-srv/',
    'limas': 'limas/',
    'axes-home': 'axes-home/'
}
updated_component_paths = False

with open(utils.COMPONENTCFG_FILE, 'r') as f:
    component_opts = json.load(f)

for (key, value) in paths.iteritems():
    if key not in component_opts['paths'] or component_opts['paths'][key] == default_val:
        component_opts['paths'][key] = value
        updated_component_paths = True

if updated_component_paths:
    with open(utils.COMPONENTCFG_FILE, 'w') as f:
        json.dump(component_opts, f,
                  sort_keys=True,
                  indent=4,
                  separators=(',', ': '))
        f.write('\n')
