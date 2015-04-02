# utils.py
# ------------------
# Scaffolding utilities for AXES-LITE

import os
import sys
import json
import contextlib
import subprocess

import logging
log = logging.getLogger(__name__)


COMPONENT_CFGS_FILE = 'config.json'
COMPONENT_CFGS_FILE_TEMPLATE = 'config.json.template'


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


def load_component_cfgs(base_path):

    with open(COMPONENT_CFGS_FILE, 'r') as f:
        component_cfgs = json.load(f)

    # convert all component paths to absolute paths
    for (key, value) in component_cfgs['components'].iteritems():
        if value and not os.path.isabs(value):
            component_cfgs['components'][key] = os.path.normpath(os.path.join(base_path, value))

    for (key, value) in component_cfgs['collection']['paths'].iteritems():
        if value and not os.path.isabs(value):
            component_cfgs['collection']['paths'][key] = os.path.normpath(os.path.join(base_path, value))

    return component_cfgs


def ensure_fname_path_exists(fname):

    try:
        os.makedirs(os.path.dirname(fname))
    except os.error:
        pass


def touch_dir(path, token):

    fname = os.path.join(path, '.pytouch.' + token)
    ensure_fname_path_exists(fname)

    exists = os.path.exists(fname)

    with open(fname, 'a'):
        os.utime(fname, None)

    return exists


def copy_replace(src, dst, repl):

    for line in src:
        for pat,rep in repl:
            if pat in line:
                line = line.replace(pat, rep)

        dst.write(line)


def write_template(templates_dir, infile, outfile, settings):

    with open(os.path.join(templates_dir, infile)) as f:
        template = f.read()

    text = template.format(**settings)

    with open(outfile, 'w') as f:
        f.write(text)


def subproc_call_check(cmd, shell=False):

    if subprocess.call(cmd, shell=shell) != 0:
        raise RuntimeError('Call ended with non-zero exit code!')
