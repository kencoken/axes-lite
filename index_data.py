# index_data.py
# ------------------
# Index data for use with AXES-LITE - see README.md for details

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("index_data")

import os
import sys
import subprocess
import argparse
import tarfile
import urlparse
from scaffoldutils import utils


def index_cpuvisor(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    index_dir = os.path.join(collection['paths']['index_data'], 'cpuvisor-srv')

    # ensure index directory exists
    try:
        os.makedirs(index_dir)
    except os.error:
        pass

    cpuvisortls = utils.import_python_module_from_path(component_paths['cpuvisor-srv'],
                                                       'download_data')

    cpuvisorutil = utils.import_python_module_from_path(os.path.join(component_paths['cpuvisor-srv'], 'utils'),
                                                        'generate_imagelist')

    # prepare paths
    log.info('[cpuvisor] Determining dataset paths...')

    dataset_keyframes_path = os.path.join(collection['paths']['private_data'], 'keyframes')

    dataset_im_paths_file = os.path.join(index_dir, 'dsetpaths_%s.txt' % collection['name'])
    dataset_feats_file = os.path.join(index_dir, 'dsetfeats_%s.binaryproto' % collection['name'])

    # generate filelist for dataset
    if not os.path.exists(dataset_im_paths_file):
        log.info('[cpuvisor] Generating dataset filelist...')
        cpuvisorutil.generate_imagelist(dataset_im_paths_file, dataset_keyframes_path)


    # update config with paths
    log.info('[cpuvisor] Updating config with dataset paths...')
    config_file_path = os.path.join(component_paths['cpuvisor-srv'],
                                    'config.%s.prototxt' % collection['name'])

    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'preproc_config.dataset_im_paths',
                                 dataset_im_paths_file,
                                 config_file_path)
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'preproc_config.dataset_im_base_path',
                                 dataset_keyframes_path,
                                 config_file_path)
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'preproc_config.dataset_feats_file',
                                 dataset_feats_file,
                                 config_file_path)

    # compute/download features for dataset

    def download_feats(collection_name, fname):

        precomputed_feat_urls = {
            'cAXESOpen': 'http://www.robots.ox.ac.uk/~vgg/software/deep_eval/releases/dsetfeats_cAXESOpen_VGG_CNN_M_128.tgz'
        }

        if collection_name not in precomputed_feat_urls:
            return False
        else:
            url = precomputed_feat_urls[collection_name]
            log.info('[cpuvisor] Downloading features for dataset...')
            log.info('[cpuvisor] URL is: %s' % url)

            (target_path, target_fname) = os.path.split(fname)

            with utils.make_temp_directory() as temp_dir:
                tarball_file_ext = os.path.splitext(urlparse.urlparse(url).path)[1]
                tarball_fname = os.path.join(temp_dir, 'feats' + tarball_file_ext)
                utils.subproc_call_check(['wget -O %s %s' % (tarball_fname, url)], shell=True)

                with tarfile.open(tarball_fname) as tar:
                    tar_ifos = {x.name: x for x in tar.getmembers()}

                    if target_fname not in tar_ifos:
                        raise RuntimeError('Precomputed feature tarball does not contain required file')
                    else:
                        tar.extractall(target_path, [tar_ifos[target_fname]])
                        return True

    def compute_feats(base_dir, collection_name):

        log.info('[cpuvisor] Computing features for dataset...')
        with utils.change_cwd(os.path.join(base_dir, 'bin')):
            utils.subproc_call_check([
                './cpuvisor_preproc',
                '--config_path', '../config.%s.prototxt' % collection_name,
                '--nonegfeats'
            ])

    if not os.path.exists(dataset_feats_file):
        if not download_feats(collection['name'], dataset_feats_file):
            compute_feats(component_paths['cpuvisor-srv'],
                          component_cfgs['collection']['name'])


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
        subprocess.call(cmd)

        # index video-level metatada
        print os.path.join(data['private_data'], 'metadata')
        subprocess.call(["scripts/integration/index_meta.py",
                         conf_fn,
                         collection,
                         os.path.join(data['private_data'], 'metadata')])

        # index shot and keyframe data
        cmd = ["scripts/integration/index_shots_from_timings.py",
               conf_fn,
               collection,
               os.path.join(data['private_data'], 'shottimings')]
        subprocess.call(cmd)

        # index shot and keyframe data
        cmd = ["bin/limas",
               'normalize',
               conf_fn ]
        subprocess.call(cmd)

        # index shot and keyframe data
        cmd = ["bin/limas",
               'indexASR',
               conf_fn ]
        subprocess.call(cmd)


# main entry point
# ................

def main(component_name=None):

    log.info('Loading component configuration...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    component_cfgs = utils.load_component_cfgs(file_dir)

    def index(name, func):
        path = component_cfgs['components'][name]
        if path and os.path.isdir(path):
            log.info('Indexing component: %s...', name)
            func(file_dir, component_cfgs)

    # Index components

    components = {
        'cpuvisor-srv': index_cpuvisor,
        'limas': index_limas
    }

    if not component_name:
        log.info('Indexing all components...')
        for name, func in components.iteritems():
            index(name, func)
    else:
        if component_name not in components:
            raise RuntimeError('Could not find component: %s' % component_name)
        index(component_name, components[component_name])


if __name__ == "__main__":

    component_name = None
    if len(sys.argv) > 1:
        component_name = sys.argv[1]

    main(component_name)
