#!/usr/bin/env python

# link_components.py
# ------------------
# Link together components of AXES-LITE - see README.md for details

import os, stat
import subprocess
import shutil
from scaffoldutils import utils

import logging
log = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', level=logging.DEBUG)


def prepare_cpuvisor(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    index_dir = os.path.join(collection['paths']['index_data'], 'cpuvisor-srv')
    templates_dir = 'templates/cpuvisor-srv/'
    path = component_paths['cpuvisor-srv']
    
    cpuvisortls = utils.import_python_module_from_path(component_paths['cpuvisor-srv'],
                                                       'download_data')

    # prepare endpoints and paths

    models_path = os.path.join(component_paths['cpuvisor-srv'], 'model_data')

    negimgs_path = os.path.join(component_paths['cpuvisor-srv'],
                                'server_data', 'neg_images')
    negidx_path = os.path.join(component_paths['cpuvisor-srv'],
                                'server_data', 'negpaths.txt')

    negfeats_path = os.path.join(component_paths['cpuvisor-srv'],
                                 'server_data', 'negfeats.binaryproto')

    server_endpoint = 'tcp://127.0.0.1:%d' % links['cpuvisor-srv']['server_port']
    notify_endpoint = 'tcp://127.0.0.1:%d' % links['cpuvisor-srv']['notify_port']

    image_cache_path = os.path.join(index_dir, 'cache', 'downloaded')
    rlist_cache_path = os.path.join(index_dir, 'cache', 'rlists')

    # prepare config
    log.info('[cpuvisor] Preparing config...')

    template_config = os.path.join(templates_dir, 'config.prototxt')
    output_config = os.path.join(component_paths['cpuvisor-srv'], 'config.%s.prototxt' % collection['name'])  

    replace_patterns = {
        '<MODELS_PATH>': models_path,
        '<NEG_IM_PATH>': negimgs_path,
        '<NEG_IM_INDEX>': negidx_path,
        '<NEG_FEATS_FILE>': negfeats_path,
        '<SERVER_ENDPOINT>': server_endpoint,
        '<NOTIFY_ENDPOINT>': notify_endpoint,
        '<IMAGE_CACHE_PATH>': image_cache_path,
        '<RLIST_CACHE_PATH>': rlist_cache_path
    }
    replace_patterns = list(replace_patterns.iteritems())

    with open(template_config, 'r') as src_f:
        with open(output_config, 'w') as dst_f:
            utils.copy_replace(src_f, dst_f, replace_patterns)

    # prepare start
    log.info('[cpuvisor] Preparing start script...')

    settings = { 'name': component_cfgs['collection']['name'] }
    #settings.update(component_cfgs)

    def write_template(infile, outfile):
        with open(os.path.join(templates_dir, infile)) as f:
            template = f.read()
        text = template.format(**settings)
        with open(outfile, 'w') as f:
            f.write(text)

    def write_start_script():
        outf = os.path.join(path, 'start.sh')
        write_template('start.sh', outf)
        os.chmod(outf, 0755)
        
    write_start_script()

    # download models

    # log.info('[cpuvisor] Downloading models...')
#     download_models(target_dir)
#
#     # download features for negative images
#
#     log.info('[cpuvisor] Attempting to download features for negative images...')
#     if not cpuvisortls.download_neg_feats(negfeats_path):
#
#         # if no features could be downloaded, compute features using negative images instead
#         log.info('[cpuvisor] Could not download negative features - downloading negative training images instead...')
#         cpuvisortls.download_neg_images(negimgs_path)
#
#         log.info('[cpuvisor] Computing features for negative images...')
#         with utils.change_cwd(os.path.join(component_paths['cpuvisor-srv'], 'bin')):
#             subprocess.call(["cpuvisor_preproc", "--nodsetfeats"])


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
             os.path.join(collection['paths']['index_data'], 'limas')),
            ('<CPUVISOR_PORT>',
             str(links['cpuvisor-srv']['server_port'])),
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
         str(links['imsearch-tools']['server_port'])),
        # AXES-HOME
        ('<AXES-HOME>',
         components['axes-home']),
        # AXES-RESEARCH
        ('<AXES-RESEARCH>',
         components['axes-research']),
        # NGINX
        ('<NGINX>',
         components['nginx'] or ''),
    ]

    with open('templates/supervisor/supervisor.conf.template', 'r') as src_f:
        with open('supervisor.conf', 'w') as dst_f:
            utils.copy_replace(src_f, dst_f, set_env_replace_patterns)


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
        'service_url': 'http://localhost:{}/json-rpc'.format(limas_port),
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
        outf = os.path.join(axes_home_path, 'nginx.conf')
        write_template('nginx.conf', outf)

    def write_start_script():
        outf = os.path.join(axes_home_path, 'start.sh')
        write_template('start.sh', outf)
        os.chmod(outf, 0755)

    write_server_settings()
    write_nginx_config()
    write_start_script()
    
def prepare_axes_research(base_path, component_cfgs):
    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    templates_dir = 'templates/axes-research/'
    path = component_paths['axes-research']
    limas_port = links['limas']['server_port']
    
    def gen_django_secret_key():
        import random
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join([random.SystemRandom().choice(chars) for i in range(50)])

    settings = {
        'service_url': 'http://localhost:{}/json-rpc'.format(limas_port),
        'axes_research_path': path,
        'collection_name': collection['name'],
        'secret_key': gen_django_secret_key()
    }
    settings.update(links['axes-research'])
    
    def write_template(infile, outfile):
        with open(templates_dir + infile) as f:
            template = f.read()
        text = template.format(**settings)
        with open(outfile, 'w') as f:
            f.write(text)
            
    def write_server_settings():
        outf = os.path.join(path, 'axesresearch/settings/local.py')
        write_template('local.py', outf)

    def write_nginx_config():
        outf = os.path.join(path, 'nginx.conf')
        write_template('nginx.conf', outf)

    def write_start_script():
        outf = os.path.join(path, 'start.sh')
        write_template('start.sh', outf)
        os.chmod(outf, 0755)
        
    def ensure_dir(path):
        if not os.path.isdir(path):
            os.makedirs(path)
            
    def collect_static_files():
        activate_cmd = ". ./venv/bin/activate"
        collect_cmd = "echo yes | python manage.py collectstatic"
        with utils.change_cwd(path):
            cmd = collect_cmd
            if os.path.isdir("venv"):
                cmd = activate_cmd + " && " + collect_cmd
            os.system(cmd)
    
    log.info('[axes-research] Preparing config...')
    ensure_dir(os.path.join(path, 'www/static'))
    ensure_dir(os.path.join(path, 'www/media'))
    write_server_settings()
    collect_static_files()
    write_nginx_config()
    write_start_script()

def prepare_imsearch_tools(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    templates_dir = 'templates/imsearch-tools/'

    log.info('[imsearch-tools] Preparing config...')

    path = component_paths['imsearch-tools']

    # Combine settings to pass to template generators
    settings = { }
    settings.update(links['imsearch-tools'])

    def write_template(infile, outfile):
        with open(templates_dir + infile) as f:
            template = f.read()
        text = template.format(**settings)
        with open(outfile, 'w') as f:
            f.write(text)

    def write_start_script():
        outf = os.path.join(path, 'start.sh')
        write_template('start.sh', outf)
        os.chmod(outf, 0755)
        
    write_start_script()

def prepare_nginx(base_path, component_cfgs):

    links = component_cfgs['links']
    collection = component_cfgs['collection']['name']
    components = component_cfgs['components']

    replace_patterns = {
        '<AXES-HOME>': components['axes-home'],
        '<AXES-RESEARCH>': components['axes-research'],
        '<NGINX_PORT>': str(links['nginx']['server_port']),
        '<HOME>': base_path
    }
    replace_patterns = list(replace_patterns.iteritems())
    
    with open('templates/nginx/nginx.conf', 'r') as src_f:
        with open(os.path.join(components['nginx'], 'conf', 'nginx.conf'), 'w') as dst_f:
            utils.copy_replace(src_f, dst_f, replace_patterns)

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
        
    if os.path.isdir(component_cfgs['components']['axes-research']):
        log.info('Preparing axes-research component...')
        prepare_axes_research(file_dir, component_cfgs)
        
    if (component_cfgs['components']['nginx'] and 
        os.path.isdir(component_cfgs['components']['nginx'])):
        log.info('Preparing nginx component...')
        prepare_nginx(file_dir, component_cfgs)
        
    if os.path.isdir(component_cfgs['components']['imsearch-tools']):
        log.info('Preparing imsearch-tools component...')
        prepare_imsearch_tools(file_dir, component_cfgs)

    log.info('Preparing supervisor configuration...')
    prepare_supervisor(file_dir, component_cfgs)
