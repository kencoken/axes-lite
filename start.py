# start.py
# ------------------
# Start AXES-LITE server - see README.md for details

import os
import subprocess
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig()


def start_cpuvisor(base_path, componentcfg):
    with utils.change_cwd(os.path.join(componentcfg['paths']['cpuvisor-srv'], 'utils')):
        subprocess.call('./start_service.sh', shell=True)


def stop_cpuvisor(base_path, componentcfg):
    with utils.change_cwd(os.path.join(componentcfg['paths']['cpuvisor-srv'], 'utils')):
        subprocess.call('./stop_service.sh', shell=True)


def start_limas(base_path, componentcfg):
    pass


def start_axes_home(base_path, componentcfg):
    pass

# main entry point
# ................

if __name__ == "__main__":

    log.info('Loading component paths...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    componentcfg = utils.load_componentcfg(file_dir)

    log.info('Starting cpuvisor-srv component...')
    start_cpuvisor(file_dir, componentcfg)

    log.info('Starting limas component...')
    start_limas(file_dir, componentcfg)

    log.info('Starting axes-home component...')
    start_axes_home(file_dir, componentcfg)
