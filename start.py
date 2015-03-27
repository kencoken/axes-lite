# start.py
# ------------------
# Start AXES-LITE server - see README.md for details

import os
import subprocess
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig()


def start_cpuvisor(base_path, component_cfgs):
    with utils.change_cwd(os.path.join(component_cfgs['paths']['cpuvisor-srv'], 'utils')):
        subprocess.call('./start_service.sh', shell=True)


def stop_cpuvisor(base_path, component_cfgs):
    with utils.change_cwd(os.path.join(component_cfgs['paths']['cpuvisor-srv'], 'utils')):
        subprocess.call('./stop_service.sh', shell=True)


def start_imsearch_tools(base_path, component_cfgs):
    with utils.change_cwd(os.path.join(component_cfgs['paths']['imsearch-tools'], 'utils')):
        subprocess.call(['./start_server.sh', component_cfgs['links']['imsearch-tools']['server_port']],
                        shell=True)


def start_limas(base_path, component_cfgs):
    pass


def start_axes_home(base_path, component_cfgs):
    pass

# main entry point
# ................

if __name__ == "__main__":

    log.info('Loading component paths...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    component_cfgs = utils.load_component_cfgs(file_dir)

    log.info('Starting cpuvisor-srv component...')
    start_cpuvisor(file_dir, component_cfgs)

    log.info('Starting imsearch-tools component...')
    start_imsearch_tools(file_dir, component_cfgs)

    log.info('Starting limas component...')
    start_limas(file_dir, component_cfgs)

    log.info('Starting axes-home component...')
    start_axes_home(file_dir, component_cfgs)
