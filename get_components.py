# get_components.py
# -----------------
# Get AXES-LITE components and store paths - see README.md for details

import os
import subprocess
import json
import pprint
from scaffoldutils import utils

# update component_paths.json with paths if is default value

# default_val = '<PATH>'
# component_paths = {
#     'cpuvisor-srv': 'cpuvisor-srv/',
#     'imsearch-tools': 'imsearch-tools/',
#     'limas': 'limas/',
#     'axes-home': 'axes-home/'
# }
#
#
#
# for (key, value) in component_paths.iteritems():
#
#     if (key not in component_opts['components']
#         or component_opts['components'][key] == default_val):
#
#         component_opts['components'][key] = value
#
# collection_paths = {
#     'public_data': 'public/',
#     'private_data': 'private/',
#     'index_data': 'index/',
# }
#
# for (key, value) in collection_paths.iteritems():
#
#     if (key not in component_opts['collection']['paths']
#         or component_opts['collection']['paths'][key] == default_val):
#
#         component_opts['collection']['paths'][key] = value
#
#         if not os.path.isdir(value):
#           os.mkdir(value)
#
# # write away changes
#
# with open(utils.COMPONENT_CFGS_FILE, 'w') as f:
#     json.dump(component_opts, f,
#               sort_keys=True,
#               indent=4,
#               separators=(',', ': '))
#     f.write('\n')

# clone components

# TODO: should download a specific tag

with open(utils.COMPONENT_CFGS_FILE, 'r') as f:
    component_opts = json.load(f)

ensure_dirs = [ component_opts['collection']['paths']['private'], 
                component_opts['collection']['paths']['public'], 
                component_opts['collection']['paths']['index'], 
                'logs' ]
for d in ensure_dirs:
  if not os.path.isdir(d):
    os.mkdir(d)

if not os.path.isdir(component_opts['components']['cpuvisor-srv']):
    subprocess.call(['git clone git@github.com:kencoken/cpuvisor-srv.git',
                     component_opts['components']['cpuvisor-srv']], shell=True)
    with utils.change_cwd('cpuvisor-srv'):
        subprocess.call('git checkout al-integration-prep', shell=True) # TODO: remove this custom branch

if not os.path.isdir(component_opts['components']['imsearch-tools']):
    subprocess.call(['git clone git@github.com:kencoken/imsearch-tools.git',
                     component_opts['components']['imsearch-tools']], shell=True)

if not os.path.isdir(component_opts['components']['limas']):
    subprocess.call(['hg clone ssh://hg@bitbucket.org/alyr/limas',
                     component_opts['components']['limas']], shell=True)

if not os.path.isdir(component_opts['components']['axes-home']):
    subprocess.call(['git clone git@bitbucket.org:kevinmcguinness/axes-home.git',
                     component_opts['components']['axes-home']], shell=True)
