# link_components.py
# ------------------
# Link together components of AXES-LITE - see README.md for details

import os
import subprocess
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig()


CPUVISOR_DOWNLOAD_NEG_FEATS_URL = ""


def prepare_cpuvisor(base_path, componentcfg):

    cpuvisortls = utils.import_python_module_from_path(componentcfg['paths']['cpuvisor-srv'],
                                                       'download_data')

    # prepare config
    log.info('[cpuvisor] Preparing config...')
    cpuvisortls.prepare_config_proto(componentcfg['paths']['cpuvisor-srv'])

    # set endpoints
    cpuvisortls.set_config_field(componentcfg['paths']['cpuvisor-srv'],
                                 'server_config.server_endpoint',
                                 componentcfg['links']['cpuvisor-srv']['server_endpoint'])
    cpuvisortls.set_config_field(componentcfg['paths']['cpuvisor-srv'],
                                 'server_config.notify_endpoint',
                                 componentcfg['links']['cpuvisor-srv']['notify_endpoint'])

    # download neg images
    log.info('[cpuvisor] Downloading negative training images...')
    target_dir = os.path.join(componentcfg['paths']['cpuvisor-srv'], 'server_data', 'neg_images')
    download_neg_images(target_dir)

    # download models
    log.info('[cpuvisor] Downloading models...')
    target_dir = os.path.join(componentcfg['paths']['cpuvisor-srv'], 'model_data')
    download_models(target_dir)

    if CPUVISOR_DOWNLOAD_NEG_FEATS_URL:
        # download features for negative images
        log.info('[cpuvisor] Dowloading features for negative images...')
        negfeats_path = os.path.join(componentcfg['paths']['cpuvisor-srv'],
                                     'server_data', 'negfeats.binaryproto')

        cpuvisortls.set_config_field(componentcfg['paths']['cpuvisor-srv'],
                                     'preproc_config.neg_feats_file',
                                     negfeats_path)

        cpuvisortls.download_url(CPUVISOR_DOWNLOAD_NEG_FEATS_URL,
                                 negfeats_path)

    else:
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
