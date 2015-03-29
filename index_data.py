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


def index_cpuvisor(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    index_dir = os.path.join(collection['paths']['index_data'], 'cpuvisor-srv')

    cpuvisortls = utils.import_python_module_from_path(component_paths['cpuvisor-srv'],
                                                       'download_data')

    cpuvisorutil = utils.import_python_module_from_path(os.path.join(component_paths['cpuvisor-srv'], 'utils'),
                                                        'generate_imagelist')

    # prepare paths
    log.info('[cpuvisor] Determining dataset paths...')

    dataset_keyframes_path = os.path.join(collection['paths']['private_data'], 'keyframes')

    dataset_im_paths_file = os.path.join(index_dir, 'dsetpaths_%s.txt' % collection['name'])
    dataset_feats_file = os.path.join(index_dir, 'dsetfeats_%s.binaryproto' % collection['name'])

    # ensure directories exist
    ensure_fname_path_exists(dataset_im_paths_file)
    ensure_fname_path_exists(dataset_feats_file)

    # generate filelist for dataset
    log.info('[cpuvisor] Generating dataset filelist...')
    cpuvisorutil.generate_imagelist(dataset_im_paths_file, dataset_keyframes_path)


    # update config with paths
    log.info('[cpuvisor] Updating config with dataset paths...')
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'preproc_config.dataset_im_paths',
                                 dataset_im_paths_file)
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'preproc_config.dataset_im_base_path',
                                 dataset_keyframes_path)
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'preproc_config.dataset_feats_file',
                                 dataset_feats_file)

    # compute features for dataset
    log.info('[cpuvisor] Computing features for dataset...')
    with utils.change_cwd(os.path.join(component_paths['cpuvisor-srv'], 'bin')):
        subprocess.call(["cpuvisor_preproc", "--nonegfeats"])


def index_limas(base_path, component_cfgs):

    components = component_cfgs['components']
    links = component_cfgs['links']
    data = component_cfgs['collection']['paths']
    collection = component_cfgs['collection']['name']

    conf_fn = os.path.join(components['limas'], 'conf', collection + '.py')

    os.environ['PATH'] = os.environ['PATH'] + ":" + os.path.join( components['limas'], 'bin')
    with utils.change_cwd(components['limas']):
        # index main video files
        cmd = ["scripts/shotdetection/index_videos.py",
                         conf_fn,
                         collection,
                         os.path.join(data['private_data'], 'ffprobe')]
        print cmd
        subprocess.call(cmd)
        # index video-level metatada
        subprocess.call(["scripts/integration/index_meta.py",
                         conf_fn,
                         collection,
                         os.path.join(data['private_data'], 'metadata')])
        # index shot and keyframe data
        subprocess.call(["scripts/integration/index_shots_from_timings.py",
                         conf_fn,
                         collection,
                         os.path.join(data['private_data'], 'shottimings')])


# main entry point
# ................

if __name__ == "__main__":

    # dataset_list = sys.args.dataset.split('=')
    # dataset = {}
    # dataset[dataset_list[0]] = dataset_list[1]

    log.info('Loading component configuration...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    component_cfgs = utils.load_component_cfgs(file_dir)

    if os.path.isdir(component_cfgs['components']['cpuvisor-srv']):
        log.info('Indexing cpuvisor-srv component...')
        index_cpuvisor(file_dir, component_cfgs)

    if os.path.isdir(component_cfgs['components']['limas']):
        log.info('Indexing limas component...')
        index_limas(file_dir, component_cfgs)
