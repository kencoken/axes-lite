# link_components.py
# ------------------
# Link together components of AXES-LITE - see README.md for details

import os
import subprocess
import shutil
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig(filename='example.log',level=logging.DEBUG)


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
    log.info('[limas] Preparing config...')
    paths = componentcfg['paths']
    links = componentcfg['links']
    with utils.change_cwd(paths['limas']):
      utils.copyReplace(open('set_env.sh.template'), open('set_env.sh', 'w'), [
        ('<directory to limas>', paths['limas']),
        ('<name of the collection that this instance should host>', links['limas']['collection_name']),
        ('<port under which the instance should run>', str(links['limas']['limas_port'])),
        ('<directory to external data>', paths['data']),
      ])
      utils.copyReplace(open('conf/conf-template.py'), open('conf/' + links['limas']['collection_name'] + '.py', 'w'), [
        ('<COLLECTION_NAME>', links['limas']['collection_name']),
        ('<PATH_TO_WEB_ACCESSIBLE_IMAGES>', paths['collection']),
        ('<PATH_TO_INDEX_STRUCTURES>', paths['index']),
        ('<CPUVISOR_PORT>', links['limas']['cpuvisor_port']),
        ('<URL_TO_COLLECTION_PATH>', links['limas']['collection_url']),
      ])


def prepare_axes_home(base_path, componentcfg):
    pass



# main entry point
# ................

if __name__ == "__main__":
    log.info('Loading component paths...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    componentcfg = utils.load_componentcfg(file_dir)

    # log.info('Preparing cpuvisor-srv component...')
    # prepare_cpuvisor(file_dir, componentcfg)

    log.info('Preparing limas component...')
    prepare_limas(file_dir, componentcfg)

    # log.info('Preparing axes-home component...')
    # prepare_axes_home(file_dir, componentcfg)
