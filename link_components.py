# link_components.py
# ------------------
# Link together components of AXES-LITE - see README.md for details

import os
import subprocess
import shutil
import re
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', level=logging.DEBUG)


CPUVISOR_DOWNLOAD_NEG_FEATS_URL = ""


def prepare_cpuvisor(base_path, component_cfgs):

    cpuvisortls = utils.import_python_module_from_path(component_cfgs['paths']['cpuvisor-srv'],
                                                       'download_data')

    # prepare config
    log.info('[cpuvisor] Preparing config...')
    cpuvisortls.prepare_config_proto(component_cfgs['paths']['cpuvisor-srv'])

    # set endpoints
    cpuvisortls.set_config_field(component_cfgs['paths']['cpuvisor-srv'],
                                 'server_config.server_endpoint',
                                 component_cfgs['links']['cpuvisor-srv']['server_endpoint'])
    cpuvisortls.set_config_field(component_cfgs['paths']['cpuvisor-srv'],
                                 'server_config.notify_endpoint',
                                 component_cfgs['links']['cpuvisor-srv']['notify_endpoint'])

    # download neg images
    log.info('[cpuvisor] Downloading negative training images...')
    target_dir = os.path.join(component_cfgs['paths']['cpuvisor-srv'], 'server_data', 'neg_images')
    download_neg_images(target_dir)

    # download models
    log.info('[cpuvisor] Downloading models...')
    target_dir = os.path.join(component_cfgs['paths']['cpuvisor-srv'], 'model_data')
    download_models(target_dir)

    if CPUVISOR_DOWNLOAD_NEG_FEATS_URL:
        # download features for negative images
        log.info('[cpuvisor] Dowloading features for negative images...')
        negfeats_path = os.path.join(component_cfgs['paths']['cpuvisor-srv'],
                                     'server_data', 'negfeats.binaryproto')

        cpuvisortls.set_config_field(component_cfgs['paths']['cpuvisor-srv'],
                                     'preproc_config.neg_feats_file',
                                     negfeats_path)

        cpuvisortls.download_url(CPUVISOR_DOWNLOAD_NEG_FEATS_URL,
                                 negfeats_path)

    else:
        # compute features for negative images
        log.info('[cpuvisor] Computing features for negative images...')
        with utils.change_cwd(os.path.join(component_cfgs['paths']['cpuvisor-srv'], 'bin')):
            subprocess.call(["cpuvisor_preproc", "--nodsetfeats"])


def prepare_limas(base_path, component_cfgs):

    log.info('[limas] Preparing config...')

    paths = component_cfgs['paths']
    links = component_cfgs['links']
    data = component_cfgs['data']

    with utils.change_cwd(paths['limas']):
        set_env_replace_patterns = [
            ('<directory to limas>',
             paths['limas']),
            ('<name of the collection that this instance should host>',
             links['limas']['collection_name']),
            ('<port under which the instance should run>',
             str(links['limas']['server_port'])),
            ('<directory to external data>',
             data['data'])
        ]

        with open('set_env.sh.template', 'r') as src_f:
            with open('set_env.sh', 'w') as dst_f:
                utils.copy_replace(src_f, dst_f, set_env_replace_patterns)

        conf_replace_patterns = [
            ('<COLLECTION_NAME>',
             links['limas']['collection_name']),
            ('<PATH_TO_WEB_ACCESSIBLE_IMAGES>',
             data['collection']),
            ('<PATH_TO_INDEX_STRUCTURES>',
             data['index']),
            ('<CPUVISOR_PORT>',
             re.search(':([0-9]+)$', links['cpuvisor-srv']['server_endpoint']).group(1)),
            ('<URL_TO_COLLECTION_PATH>',
             links['limas']['collection_url'])
        ]

        with open('conf/conf-template.py', 'r') as src_f:
            with open('conf/' + links['limas']['collection_name'] + '.py', 'w') as dst_f:
                utils.copy_replace(src_f, dst_f, conf_replace_patterns)


def prepare_axes_home(base_path, component_cfgs):
    pass



# main entry point
# ................

if __name__ == "__main__":
    log.info('Loading component paths...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    component_cfgs = utils.load_component_cfgs(file_dir)

    log.info('Preparing cpuvisor-srv component...')
    prepare_cpuvisor(file_dir, component_cfgs)

    log.info('Preparing limas component...')
    prepare_limas(file_dir, component_cfgs)

    log.info('Preparing axes-home component...')
    prepare_axes_home(file_dir, component_cfgs)
