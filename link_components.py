#!/usr/bin/env python
"""
Link together components of AXES-LITE - see README.md for details
"""

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("link_components")

import os
import sys
from scaffoldutils import utils


def prepare_cpuvisor(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    index_dir = os.path.join(collection['paths']['index_data'], 'cpuvisor-srv')
    templates_dir = os.path.join('templates', 'cpuvisor-srv')
    path = component_paths['cpuvisor-srv']

    cpuvisortls = utils.import_python_module_from_path(component_paths['cpuvisor-srv'],
                                                       'download_data')

    if not os.path.exists(os.path.join(component_paths['cpuvisor-srv'], 'bin')):
        raise RuntimeError('[cpuvisor] Missing bin directory - compile before running link_components!')

    # prepare endpoints and paths

    models_path = os.path.join(component_paths['cpuvisor-srv'], 'model_data')

    negimgs_path = os.path.join(component_paths['cpuvisor-srv'],
                                'server_data', 'neg_images')
    negidx_path = os.path.join(component_paths['cpuvisor-srv'],
                               'negpaths.txt')

    negfeats_path = os.path.join(component_paths['cpuvisor-srv'],
                                 'server_data', 'negfeats.binaryproto')

    server_endpoint = 'tcp://127.0.0.1:%d' % links['cpuvisor-srv']['server_port']
    notify_endpoint = 'tcp://127.0.0.1:%d' % links['cpuvisor-srv']['notify_port']

    image_cache_path = os.path.join(index_dir, 'cache', 'downloaded')
    rlist_cache_path = os.path.join(index_dir, 'cache', 'rlists')

    # prepare config
    log.info('[cpuvisor] Preparing config...')

    def prepare_config():

        template_config = os.path.join(templates_dir, 'config.prototxt')
        output_config = os.path.join(component_paths['cpuvisor-srv'],
                                     'config.%s.prototxt' % collection['name'])

        # if the config file already exists, read in fields added by index_data first
        restore_fields = False

        if os.path.exists(output_config):
            restore_fields = True

            def get_field(field_name):
                return cpuvisortls.get_config_field(component_paths['cpuvisor-srv'],
                                                    field_name,
                                                    output_config)

            dataset_im_paths = get_field('preproc_config.dataset_im_paths')
            dataset_im_base_path = get_field('preproc_config.dataset_im_base_path')
            dataset_feats_file = get_field('preproc_config.dataset_feats_file')

        # write the new config file
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

        # now restore fields added by index_data if required
        if restore_fields:

            def set_field(field_name, field_value):
                cpuvisortls.set_config_field(component_paths['cpuvisor-srv'],
                                             field_name,
                                             field_value,
                                             output_config)

            set_field('preproc_config.dataset_im_paths', dataset_im_paths)
            set_field('preproc_config.dataset_im_base_path', dataset_im_base_path)
            set_field('preproc_config.dataset_feats_file', dataset_feats_file)


    prepare_config()

    # prepare start script
    log.info('[cpuvisor] Preparing start script...')

    def write_start_script():
        outf = os.path.join(path, 'start.sh')
        utils.write_template(templates_dir, 'start.sh', outf,
                             {'name': component_cfgs['collection']['name']})
        os.chmod(outf, 0755)

    write_start_script()

    # download models
    log.info('[cpuvisor] Getting models...')
    cpuvisortls.download_models(models_path)

    # download features for negative images

    if os.path.exists(negfeats_path):

        log.info('[cpuvisor] Negative feature file exists')

    else:

        log.info('[cpuvisor] Attempting to download features for negative images...')
        if not cpuvisortls.download_neg_feats(negfeats_path):

            # if no features could be downloaded, compute features using negative images instead
            log.info('[cpuvisor] Could not download negative features - downloading negative training images instead...')
            if not utils.touch_dir(negimgs_path, 'negimgs'):
                cpuvisortls.download_neg_images(negimgs_path)

            log.info('[cpuvisor] Computing features for negative images...')
            with utils.change_cwd(os.path.join(component_paths['cpuvisor-srv'], 'bin')):
                utils.subproc_call_check([
                    './cpuvisor_preproc',
                    '--config_path', '../config.%s.prototxt' % component_cfgs['collection']['name'],
                    '--nodsetfeats'
                ])


def prepare_limas(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    templates_dir = os.path.join('templates', 'limas')
    path = component_paths['limas']

    # prepare config
    log.info('[limas] Preparing config...')

    with utils.change_cwd(component_paths['limas']):
        set_env_replace_patterns = [
            ('<directory to limas>',
             component_paths['limas']),
            ('<name of the collection that this instance should host>',
             collection['name']),
            ('<port under which the instance should run>',
             str(links['limas']['server_port'])),
            ('<directory to private data>',
             collection['paths']['private_data'])
        ]

        with open('set_env.sh.template', 'r') as src_f:
            with open('set_env.sh', 'w') as dst_f:
                utils.copy_replace(src_f, dst_f, set_env_replace_patterns)

        conf_replace_patterns = {
            '<COLLECTION_NAME>': collection['name'],
            '<PATH_TO_WEB_ACCESSIBLE_IMAGES>': collection['paths']['public_data'],
            '<PATH_TO_INDEX_STRUCTURES>': os.path.join(collection['paths']['index_data'],
                                                       'limas'),
            '<CPUVISOR_PORT>': str(links['cpuvisor-srv']['server_port']),
            '<CPUVISOR_NOTIFY_PORT>': str(links['cpuvisor-srv']['notify_port']),
            '<URL_TO_COLLECTION_PATH>': collection['url'],
            '<MONGODB_PORT>': str(links['mongodb']['server_port']),
            '<IMSEARCH_PORT>': str(links['imsearch-tools']['server_port'])
        }
        conf_replace_patterns = list(conf_replace_patterns.iteritems())

        with open(os.path.join('conf', 'conf-template.py'), 'r') as src_f:
            with open(os.path.join('conf', collection['name'] + '.py'), 'w') as dst_f:
                utils.copy_replace(src_f, dst_f, conf_replace_patterns)

    # prepare start script
    log.info('[limas] Preparing start script...')

    def write_start_script():
        outf = os.path.join(path, 'start.sh')
        utils.write_template(templates_dir, 'start.sh', outf,
                             {'server_port': links['limas']['server_port'],
                              'base_dir': path,
                              'name': component_cfgs['collection']['name']})
        os.chmod(outf, 0755)

    write_start_script()


def prepare_axes_home(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    config = component_cfgs['config']
    collection = component_cfgs['collection']
    templates_dir = os.path.join('templates', 'axes-home')

    log.info('[axes-home] Preparing config...')

    axes_home_path = component_paths['axes-home']
    limas_port = links['limas']['server_port']

    # Combine settings to pass to template generators
    settings = {
        'service_url': 'http://localhost:{}/json-rpc'.format(limas_port),
        'axes_home_path': axes_home_path,
    }
    settings.update(links['axes-home'])
    settings.update(config['axes-home'])

    if settings['mount_point'].endswith(os.sep):
        settings['mount_point'] = settings['mount_point'][:-1]

    def write_server_settings():
        outf = os.path.join(axes_home_path, 'server', 'settings.cfg')
        utils.write_template(templates_dir, 'settings.cfg', outf, settings)

    def write_nginx_config():
        outf = os.path.join(axes_home_path, 'nginx.conf')
        utils.write_template(templates_dir, 'nginx.conf', outf, settings)

    def write_start_script():
        outf = os.path.join(axes_home_path, 'start.sh')
        utils.write_template(templates_dir, 'start.sh', outf, settings)
        os.chmod(outf, 0755)

    write_server_settings()
    write_nginx_config()
    write_start_script()


def prepare_axes_research(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    config = component_cfgs['config']
    collection = component_cfgs['collection']
    templates_dir = os.path.join('templates', 'axes-research')
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
    settings.update(config['axes-research'])

    def write_server_settings():
        outf = os.path.join(path, 'axesresearch', 'settings', 'local.py')
        utils.write_template(templates_dir, 'local.py', outf, settings)

    def write_nginx_config():
        outf = os.path.join(path, 'nginx.conf')
        utils.write_template(templates_dir, 'nginx.conf', outf, settings)

    def write_start_script():
        outf = os.path.join(path, 'start.sh')
        utils.write_template(templates_dir, 'start.sh', outf, settings)
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

    ensure_dir(os.path.join(path, 'www', 'static'))
    ensure_dir(os.path.join(path, 'www', 'media'))

    write_server_settings()
    collect_static_files()
    write_nginx_config()
    write_start_script()


def prepare_imsearch_tools(base_path, component_cfgs):

    component_paths = component_cfgs['components']
    links = component_cfgs['links']
    collection = component_cfgs['collection']
    templates_dir = os.path.join('templates', 'imsearch-tools')

    # prepare config
    log.info('[imsearch-tools] Preparing config...')

    path = component_paths['imsearch-tools']

    def write_start_script():
        outf = os.path.join(path, 'start.sh')
        utils.write_template(templates_dir, 'start.sh', outf,
                             {'server_port': links['imsearch-tools']['server_port']})
        os.chmod(outf, 0755)

    write_start_script()


def prepare_nginx(base_path, component_cfgs):

    links = component_cfgs['links']
    collection = component_cfgs['collection']['name']
    components = component_cfgs['components']
    templates_dir = os.path.join('templates', 'nginx')
    path = os.path.join(components['nginx'], 'conf')

    # place nginx config in root directory if directory specified by nginx does not exist
    if not os.path.isdir(path):
        path = ''

    # prepare config
    log.info('Preparing nginx config...')

    replace_patterns = {
        '<AXES-HOME>': components['axes-home'],
        '<AXES-RESEARCH>': components['axes-research'],
        '<NGINX_PORT>': str(links['nginx']['server_port']),
        '<HOME>': base_path,
        '<PUBLIC_DATA>': component_cfgs['collection']['paths']['public_data']
    }
    replace_patterns = list(replace_patterns.iteritems())

    with open(os.path.join(templates_dir, 'nginx.conf'), 'r') as src_f:
        with open(os.path.join(path, 'nginx.conf'), 'w') as dst_f:
            utils.copy_replace(src_f, dst_f, replace_patterns)


def prepare_start_script(base_path, component_cfgs):

    links = component_cfgs['links']
    components = component_cfgs['components']
    config = component_cfgs['config']
    templates_dir = os.path.join('templates')
    path = ''

    # prepare start script
    log.info('Preparing sample start script...')

    def write_mongo_start_script():
        outf = os.path.join(path, 'start_mongo.sh')
        utils.write_template(os.path.join(templates_dir, 'mongodb'), 'start_mongo.sh', outf,
                             {'mongo_path': components['mongodb'],
                              'mongo_port': links['mongodb']['server_port'],
                              'mongo_dbpath': os.path.join(component_cfgs['collection']['paths']['index_data'], 'db')})
        os.chmod(outf, 0755)

    def write_nginx_start_script():
        outf = os.path.join(path, 'start_nginx.sh')
        utils.write_template(os.path.join(templates_dir, 'nginx'), 'start_nginx.sh', outf,
                             {'nginx_path': components['nginx'],
                              'nginx_config': os.path.join(components['nginx'], 'conf', 'nginx.conf')})
        os.chmod(outf, 0755)

    def write_axeslite_start_script():
        outf = os.path.join(path, 'start.sh')
        utils.write_template(templates_dir, 'start.sh', outf,
                             {'cpuvisor-srv_path': components['cpuvisor-srv'],
                              'imsearch-tools_path': components['imsearch-tools'],
                              'limas_path': components['limas'],
                              'axes-home_path': components['axes-home'],
                              'axes-research_path': components['axes-research']})
        os.chmod(outf, 0755)

    write_mongo_start_script()
    write_nginx_start_script()
    write_axeslite_start_script()


def prepare_supervisor(base_path, component_cfgs):

    links = component_cfgs['links']
    collection = component_cfgs['collection']['name']
    components = component_cfgs['components']
    templates_dir = os.path.join('templates', 'supervisor')

    # prepare config
    log.info('Preparing supervisor configuration...')

    # TODO: add either axes-research or axes-home or both to default target
    # depending on value of config['limas']['frontend']

    set_env_replace_patterns = {
        '<INDEX_PATH>': component_cfgs['collection']['paths']['index_data'],
        '<LIMAS>': components['limas'],
        '<CPUVISOR-SRV>': components['cpuvisor-srv'],
        '<IMSEARCH-TOOLS>': components['imsearch-tools'],
        '<AXES-HOME>': components['axes-home'],
        '<AXES-RESEARCH>': components['axes-research'],
        '<NGINX>': components['nginx'] or '',
        '<MONGODB>': components['mongodb'],
        '<MONGODB_PORT': str(links['mongodb']['server_port'])
    }
    set_env_replace_patterns = list(set_env_replace_patterns.iteritems())

    with open(os.path.join(templates_dir, 'supervisord.conf.template'), 'r') as src_f:
        with open('supervisord.conf', 'w') as dst_f:
            utils.copy_replace(src_f, dst_f, set_env_replace_patterns)


# main entry point
# ................

def main(component_name=None):

    log.info('Loading component configuration...')
    file_dir = os.path.dirname(os.path.realpath(__file__))
    component_cfgs = utils.load_component_cfgs(file_dir)

    def prepare(name, func):
        path = component_cfgs['components'][name]
        if path and os.path.isdir(path):
            log.info('Preparing component: %s...', name)
            func(file_dir, component_cfgs)

    # Prepare components

    components = {
        'cpuvisor-srv': prepare_cpuvisor,
        'limas': prepare_limas,
        'axes-home': prepare_axes_home,
        'axes-research': prepare_axes_research,
        'imsearch-tools': prepare_imsearch_tools,
        'nginx': prepare_nginx
    }

    if not component_name:
        log.info('Linking all components...')
        for name, func in components.iteritems():
            prepare(name, func)

        # Prepare nginx config
        prepare_nginx(file_dir, component_cfgs)

        # Prepare screen-based launch script
        prepare_start_script(file_dir, component_cfgs)

        # Prepare supervisor
        prepare_supervisor(file_dir, component_cfgs)

    else:
        if component_name not in components:
            raise RuntimeError('Could not find component: %s' % component_name)
        prepare(component_name, components[component_name])


if __name__ == "__main__":

    component_name = None
    if len(sys.argv) > 1:
        component_name = sys.argv[1]

    main(component_name)
