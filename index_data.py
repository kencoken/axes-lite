# index_data.py
# ------------------
# Index data for use with AXES-LITE - see README.md for details

import os
import subprocess
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig()


def index_cpuvisor(base_path, component_paths,
                   dataset_name, dataset_root_path):

    cpuvisortls = utils.import_python_module_from_path(component_paths['cpuvisor-srv'],
                                                       'download_data')

    cpuvisorutil = utils.import_python_module_from_path(os.path.join(component_paths['cpuvisor-srv'], 'utils'),
                                                        'generate_imagelist')

    # compute paths
    log.info('[cpuvisor] Determining dataset paths...')
    dataset_im_paths = os.path.join(component_paths['cpuvisor-srv'],
                                    'server_data',
                                    'dsetpaths_%s.binaryproto' % dataset_name)
    dataset_feats_file = os.path.join(component_paths['cpuvisor-srv'],
                                      'server_data',
                                      'dsetfeats_%s.binaryproto' % dataset_name)

    # generate filelist for dataset
    log.info('[cpuvisor] Generating dataset filelist...')
    cpuvisorutil.generate_imagelist(dataset_im_paths, dataset_root_path)


    # update config with paths
    log.info('[cpuvisor] Updating config with dataset paths...')
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'dataset_im_paths',
                                 dataset_im_paths)
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'dataset_im_base_path',
                                 dataset_root_path)
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'dataset_feats_file',
                                 dataset_feats_file)

    # compute features for dataset
    log.info('[cpuvisor] Computing features for dataset...')
    with change_cwd_tmp(os.path.join(component_paths['cpuvisor-srv', 'bin'])):
        subprocess.call(["cpuvisor_preproc", "--nonegfeats"])


def index_limas(base_path, component_paths,
                dataset_name, dataset_root_path):
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
