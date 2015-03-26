# link_components.py
# ------------------
# Link together components of AXES-LITE - see README.md for details

import os
import subprocess
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig()


def prepare_cpuvisor(base_path, componentcfg):

    cpuvisortls = utils.import_python_module_from_path(componentcfg['paths']['cpuvisor-srv'],
                                                       'download_data')

    # prepare config
    log.info('[cpuvisor] Preparing config...')
    # cpuvisortls.prepare_config_proto(componentcfg['paths']['cpuvisor-srv'])

    # # download neg images
    # log.info('[cpuvisor] Downloading negative training images...')
    # target_dir = os.path.join(componentcfg['paths']['cpuvisor-srv'], 'server_data', 'neg_images')
    # download_neg_images(target_dir)

    # # download models
    # log.info('[cpuvisor] Downloading models...')
    # target_dir = os.path.join(componentcfg['paths']['cpuvisor-srv'], 'model_data')
    # download_models(target_dir)

    # compute features for negative images
    log.info('[cpuvisor] Computing features for negative images...')
    with utils.change_cwd(os.path.join(componentcfg['paths']['cpuvisor-srv'], 'bin')):
        subprocess.call(["cpuvisor_preproc", "--nodsetfeats"])


def prepare_limas(base_path, componentcfg):
    pass


def prepare_axes_home(base_path, componentcfg):
    pass



# main entry point
# ................

if __name__ == "__main__":

    log.info('Loading component paths...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    componentcfg = utils.load_componentcfg(file_dir)

    log.info('Preparing cpuvisor-srv component...')
    prepare_cpuvisor(file_dir, componentcfg)

    log.info('Preparing limas component...')
    prepare_limas(file_dir, componentcfg)

    log.info('Preparing axes-home component...')
    prepare_axes_home(file_dir, componentcfg)
