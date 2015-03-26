# index_data.py
# ------------------
# Index data for use with AXES-LITE - see README.md for details

import os
import subprocess
import argparse
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig()


def index_cpuvisor(base_path, componentcfg,
                   dataset_name, dataset_root_path):

    cpuvisortls = utils.import_python_module_from_path(componentcfg['paths']['cpuvisor-srv'],
                                                       'download_data')

    cpuvisorutil = utils.import_python_module_from_path(os.path.join(componentcfg['paths']['cpuvisor-srv'], 'utils'),
                                                        'generate_imagelist')

    # prepare paths
    log.info('[cpuvisor] Determining dataset paths...')

    dataset_keyframes_path = os.path.join(dataset_root_path, 'keyframes')

    dataset_im_paths = os.path.join(componentcfg['paths']['cpuvisor-srv'],
                                    'server_data',
                                    'dsetpaths_%s.binaryproto' % dataset_name)
    dataset_feats_file = os.path.join(componentcfg['paths']['cpuvisor-srv'],
                                      'server_data',
                                      'dsetfeats_%s.binaryproto' % dataset_name)

    # generate filelist for dataset
    log.info('[cpuvisor] Generating dataset filelist...')
    cpuvisorutil.generate_imagelist(dataset_im_paths, dataset_keyframes_path)


    # update config with paths
    log.info('[cpuvisor] Updating config with dataset paths...')
    cpuvisortls.set_config_field(componentcfg['paths']['cpuvisor-srv'],
                                 'preproc_config.dataset_im_paths',
                                 dataset_im_paths)
    cpuvisortls.set_config_field(componentcfg['paths']['cpuvisor-srv'],
                                 'preproc_config.dataset_im_base_path',
                                 dataset_keyframes_path)
    cpuvisortls.set_config_field(componentcfg['paths']['cpuvisor-srv'],
                                 'preproc_config.dataset_feats_file',
                                 dataset_feats_file)

    # compute features for dataset
    log.info('[cpuvisor] Computing features for dataset...')
    with utils.change_cwd(os.path.join(componentcfg['paths']['cpuvisor-srv'], 'bin')):
        subprocess.call(["cpuvisor_preproc", "--nonegfeats"])


def index_limas(base_path, componentcfg,
                dataset_name, dataset_root_path):
    pass




# main entry point
# ................

if __name__ == "__main__":

    # parse input arguments
    parser = argparse.ArgumentParser(description='Generate imagelist from directory')
    parser.add_argument('dataset_name', type=str,
                        help='Name of dataset to index')
    parser.add_argument('dataset_root_path', type=str,
                        help='Root directory of dataset in AXES format')
    args = parser.parse_args()

    dataset_list = args.dataset.split('=')
    dataset = {}
    dataset[dataset_list[0]] = dataset_list[1]

    log.info('Loading component paths...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    componentcfg = utils.load_componentcfg(file_dir)

    log.info('Indexing cpuvisor-srv component...')
    prepare_cpuvisor(file_dir, componentcfg,
                     args.dataset_name, args.dataset_root_path)

    log.info('Indexing limas component...')
    prepare_limas(file_dir, componentcfg,
                  args.dataset_name, args.dataset_root_path)
