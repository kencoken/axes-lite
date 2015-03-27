# get_components.py
# -----------------
# Get AXES-LITE components and store paths - see README.md for details

import os
import subprocess
import json
import pprint
from scaffoldutils import utils

# update component_paths.json with paths if is default value

default_val = '<PATH>'
paths = {
    'cpuvisor-srv': 'cpuvisor-srv/',
    'imsearch-tools': 'imsearch-tools/',
    'limas': 'limas/',
    'axes-home': 'axes-home/'
}

with open(utils.COMPONENT_CFGS_FILE_TEMPLATE, 'r') as f:
    component_opts = json.load(f)

for (key, value) in paths.iteritems():
    if key not in component_opts['paths'] or component_opts['paths'][key] == default_val:
        component_opts['paths'][key] = value

data_paths = {
    'data': 'data/',
    'index': 'index/',
    'collection': 'collection/',
}

for (key, value) in data_paths.iteritems():
    if key not in component_opts['data'] or component_opts['data'][key] == default_val:
        component_opts['data'][key] = value
        if not os.path.isdir(value):
          os.mkdir(value)

# write away changes

with open(utils.COMPONENT_CFGS_FILE, 'w') as f:
    json.dump(component_opts, f,
              sort_keys=True,
              indent=4,
              separators=(',', ': '))
    f.write('\n')

# clone components

# TODO: should download a specific tag

if not os.path.isdir(component_opts['paths']['cpuvisor-srv']):
    subprocess.call(['git clone git@github.com:kencoken/cpuvisor-srv.git',
                     component_opts['paths']['cpuvisor-srv']], shell=True)
    with utils.change_cwd('cpuvisor-srv'):
        subprocess.call('git checkout al-integration-prep', shell=True) # TODO: remove this custom branch

if not os.path.isdir(component_opts['paths']['imsearch-tools']):
    subprocess.call(['git clone git@github.com:kencoken/imsearch-tools.git',
                     component_opts['paths']['imsearch-tools']], shell=True)

if not os.path.isdir(component_opts['paths']['limas']):
    subprocess.call(['hg clone ssh://hg@bitbucket.org/alyr/limas',
                     component_opts['paths']['limas']], shell=True)

if not os.path.isdir(component_opts['paths']['axes-home']):
    subprocess.call(['git clone git@bitbucket.org:kevinmcguinness/axes-home.git',
                     component_opts['paths']['axes-home']], shell=True)
