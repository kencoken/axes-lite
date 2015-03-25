# index_data.py
# ------------------
# Index data for use with AXES-LITE - see README.md for details

import os
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig()


def index_cpuvisor(base_path, component_paths):
    pass

    # update config with dataset paths
    #cpuvisortls.set_config_field(component_paths['cpuvisor-srv'], 'dataset_feats_file', 'hello world')

    # compute features for dataset


def index_limas(base_path, component_paths):
    pass




# main entry point
# ................

if __name__ == "__main__":

    log.info('Loading component paths...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    component_paths = utils.load_component_paths(file_dir)

    log.info('Indexing cpuvisor-srv component...')
    prepare_cpuvisor(file_dir, component_paths)

    log.info('Indexing limas component...')
    prepare_limas(file_dir, component_paths)

    log.info('Indexing axes-home component...')
    prepare_axes_home(file_dir, component_paths)
