import os
import json
import pprint

# clone components

if not os.path.isdir('cpuvisor-srv'):
    os.system('git clone git@github.com:kencoken/cpuvisor-srv.git')

if not os.path.isdir('limas'):
    os.system('hg clone ssh://hg@bitbucket.org/alyr/limas')

if not os.path.isdir('axes-home'):
    os.system('git clone git@bitbucket.org:kevinmcguinness/axes-home.git')

# update component_paths.json with paths if is default value

default_val = '<PATH>'
paths = {
    'cpuvisor-srv': 'cpuvisor-srv/',
    'limas': 'limas/',
    'axes-home': 'axes-home/'
}
updated_component_paths = False

with open('component_paths.json', 'r') as f:
    components = json.load(f)

for (key, value) in paths.iteritems():
    if key not in components or components[key] == default_val:
        components[key] = value
        updated_component_paths = True

if updated_component_paths:
    with open('component_paths.json', 'w') as f:
        json.dump(components, f,
                  sort_keys=True,
                  indent=4,
                  separators=(',', ': '))
        f.write('\n')
