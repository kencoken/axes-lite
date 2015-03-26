# utils.py
# ------------------
# Scaffolding utilities for AXES-LITE

import os
import sys
import json
import contextlib

import logging
log = logging.getLogger(__name__)
logging.basicConfig()


COMPONENTCFG_FILE = 'componentcfg.json'


def import_python_module_from_path(path, module_name):

    module_init_file = os.path.join(path, '__init__.py')
    is_already_module = os.path.exists(module_init_file)
    should_add_to_path = ((os.path.normpath(os.getcwd()) != os.path.normpath(path)) and
                          not path in sys.path)

    if not is_already_module:
        open(module_init_file, 'a').close()
    if should_add_to_path:
        sys.path.insert(1, path)

    module = __import__(module_name)

    if not is_already_module:
        try:
            os.remove(module_init_file)
        except OSError:
            pass
    if should_add_to_path and path in sys.path:
        sys.path.remove(path)

    return module


@contextlib.contextmanager
def change_cwd(path):
    old_cwd = os.getcwd()
    os.chdir(path)

    yield

    os.chdir(old_cwd)


def load_componentcfg(base_path):

    with open(COMPONENTCFG_FILE, 'r') as f:
        componentcfg = json.load(f)

    # convert all component paths to absolute paths
    for (key, value) in componentcfg['paths'].iteritems():
        if not os.path.isabs(value):
            componentcfg['paths'][key] = os.path.normpath(os.path.join(base_path, value))

    return componentcfg


def copy_replace(src, dst, repl):

  for line in src:
    for pat,rep in repl:
      if pat in line:
        line = line.replace(pat, rep)
    dst.write(line)
