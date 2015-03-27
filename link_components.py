# link_components.py
# ------------------
# Link together components of AXES-LITE - see README.md for details

import os
import subprocess
import shutil
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', level=logging.DEBUG)


CPUVISOR_DOWNLOAD_NEG_FEATS_URL = ""


def prepare_cpuvisor(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']

    cpuvisortls = utils.import_python_module_from_path(component_paths['cpuvisor-srv'],
                                                       'download_data')

    # prepare config
    log.info('[cpuvisor] Preparing config...')
    cpuvisortls.prepare_config_proto(component_paths['cpuvisor-srv'])

    # set endpoints
    server_endpoint = 'tcp://127.0.0.1:%d' % links['cpuvisor-srv']['server_port']
    notify_endpoint = 'tcp://127.0.0.1:%d' % links['cpuvisor-srv']['notify_port']

    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'server_config.server_endpoint',
                                 links['cpuvisor-srv']['server_endpoint'])
    cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                 'server_config.notify_endpoint',
                                 links['cpuvisor-srv']['notify_endpoint'])

    # download neg images
    log.info('[cpuvisor] Downloading negative training images...')
    target_dir = os.path.join(component_paths['cpuvisor-srv'], 'server_data', 'neg_images')
    download_neg_images(target_dir)

    # download models
    log.info('[cpuvisor] Downloading models...')
    target_dir = os.path.join(component_paths['cpuvisor-srv'], 'model_data')
    download_models(target_dir)

    if CPUVISOR_DOWNLOAD_NEG_FEATS_URL:
        # download features for negative images
        log.info('[cpuvisor] Dowloading features for negative images...')
        negfeats_path = os.path.join(component_paths['cpuvisor-srv'],
                                     'server_data', 'negfeats.binaryproto')

        cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                     'preproc_config.neg_feats_file',
                                     negfeats_path)

        cpuvisortls.download_url(CPUVISOR_DOWNLOAD_NEG_FEATS_URL,
                                 negfeats_path)

    else:
        # compute features for negative images
        log.info('[cpuvisor] Computing features for negative images...')
        with utils.change_cwd(os.path.join(component_paths['cpuvisor-srv'], 'bin')):
            subprocess.call(["cpuvisor_preproc", "--nodsetfeats"])


def prepare_limas(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']

    log.info('[limas] Preparing config...')

    with utils.change_cwd(component_paths['limas']):
        set_env_replace_patterns = [
            ('<directory to limas>',
             component_paths['limas']),
            ('<name of the collection that this instance should host>',
             collection['name']),
            ('<port under which the instance should run>',
             str(links['limas']['server_port'])),
            ('<directory to external data>',
             collection['paths']['private_data'])
        ]

        with open('set_env.sh.template', 'r') as src_f:
            with open('set_env.sh', 'w') as dst_f:
                utils.copy_replace(src_f, dst_f, set_env_replace_patterns)

        conf_replace_patterns = [
            ('<COLLECTION_NAME>',
             collection['name']),
            ('<PATH_TO_WEB_ACCESSIBLE_IMAGES>',
             collection['paths']['public_data']),
            ('<PATH_TO_INDEX_STRUCTURES>',
             collection['paths']['index_data']),
            ('<CPUVISOR_PORT>',
             links['cpuvisor-srv']['server_port']),
            ('<URL_TO_COLLECTION_PATH>',
             links['axes-home']['collection_url'])
        ]

        with open('conf/conf-template.py', 'r') as src_f:
            with open('conf/' + collection['name'] + '.py', 'w') as dst_f:
                utils.copy_replace(src_f, dst_f, conf_replace_patterns)

def prepare_supervisor(base_path, component_cfgs):
    links = component_cfgs['links']
    collection = component_cfgs['collection']['name']
    components = component_cfgs['components']
    set_env_replace_patterns = [
        # limas
        ('<LIMAS>',
         components['limas']),
        ('<LIMAS_PORT>',
         str(links['limas']['server_port'])),
        ('<LIMAS_CONF>',
         os.path.join(components['limas'], 'conf', collection + '.py')),
        # cpu visor
        ('<CPUVISOR-SRV>',
        components['cpuvisor-srv']), 
        ('<CPUVISOR-SRV_PORT>',
         str(links['cpuvisor-srv']['server_port'])),
        # image search
        ('<IMSEARCH-TOOLS>',
        components['imsearch-tools']),
        ('<IMSEARCH-TOOLS_PORT>',
         str(links['imsearch-tools']['server_port']))
    ]

    with open('supervisor.conf.template', 'r') as src_f:
        with open('supervisor.conf', 'w') as dst_f:
            utils.copy_replace(src_f, dst_f, set_env_replace_patterns)
    pass

def prepare_axes_home(base_path, component_cfgs):
    
    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    templates_dir = 'templates/axes-home/'

    log.info('[axes-home] Preparing config...')
    
    axes_home_path = component_paths['axes-home']
    limas_port = links['limas']['server_port']
    
    # Combine settings to pass to template generators
    settings = {
        'service_url': 'http://localhost:{}/json_rpc'.format(limas_port),
        'axes_home_path': axes_home_path,
    }
    settings.update(links['axes-home'])
    
    if settings['mount_point'].endswith('/'):
        settings['mount_point'] = settings['mount_point'][:-1]
    
    def write_template(infile, outfile):
        with open(templates_dir + infile) as f:
            template = f.read()
        text = template.format(**settings)
        with open(outfile, 'w') as f:
            f.write(text)
    
    def write_server_settings():
        outf = os.path.join(axes_home_path, 'server', 'settings.cfg') 
        write_template('settings.cfg', outf)
            
    def write_nginx_config():
        write_template('nginx.conf', 'nginx.conf')
        
    def write_start_script():
        outf = os.path.join(axes_home_path, 'start.sh') 
        write_template('start.sh', outf)
    
    write_server_settings()
    write_nginx_config()
    write_start_script()
    
    

# main entry point
# ................

if __name__ == "__main__":
    log.info('Loading component configuration...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    component_cfgs = utils.load_component_cfgs(file_dir)

    if os.path.isdir(component_cfgs['components']['cpuvisor-srv']):
        log.info('Preparing cpuvisor-srv component...')
        prepare_cpuvisor(file_dir, component_cfgs)

    if os.path.isdir(component_cfgs['components']['limas']):
        log.info('Preparing limas component...')
        prepare_limas(file_dir, component_cfgs)

    if os.path.isdir(component_cfgs['components']['axes-home']):
        log.info('Preparing axes-home component...')
        prepare_axes_home(file_dir, component_cfgs)
        
    log.info('Preparing supervisor configuration...')
    prepare_supervisor(file_dir, component_cfgs)
