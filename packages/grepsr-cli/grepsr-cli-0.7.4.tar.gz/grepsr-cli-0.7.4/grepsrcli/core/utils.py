import json
import subprocess
from pathlib import Path
from os import listdir, path, mkdir
import re
from jinja2 import Template
from .config import load_config
from terminaltables import SingleTable
from .message_log import Log


def get_plugin_path(plugin_name, type='php', all_types=False):
    """ returns the path of the plugin if plugin name exist

    Args:
        plugin_name (str): name of the service plugin .
        type (str, optional): php|py|node. Defaults to 'php'.
        all_types: retuns the path regardless the plugin types i.e php, py and node
    """
    config = load_config('config.yml')
    if all_types == False:
        if type == 'php':
            if _generate_plugin_path(plugin_name, config['php']['paths']):
                return _generate_plugin_path(plugin_name, config['php']['paths'])
            else:
                return False
        elif type == 'node':
            if _generate_plugin_path(plugin_name, config['node']['paths']):
                return _generate_plugin_path(plugin_name, config['node']['paths'])
            else:
                return False
        elif type == 'py':
            if _generate_plugin_path(plugin_name, config['python']['paths']):
                return _generate_plugin_path(plugin_name, config['python']['paths'])
            else:
                return False
        elif type == 'php_next':
            if _generate_plugin_path(plugin_name, config['php_next']['paths']):
                return _generate_plugin_path(plugin_name, config['php_next']['paths'])
            else:
                return False
        elif type == 'node_next':
            if _generate_plugin_path(plugin_name, config['node_next']['paths']):
                return _generate_plugin_path(plugin_name, config['node_next']['paths'])
            else:
                return False
        else:
            Log.error("Invalid params for type.")
            return False
    else:
        # todo: do not hardcode this
        base_paths_list = [
            config['php']['paths'] if 'php' in config else None,
            config['node']['paths'] if 'node' in config else None,
            config['python']['paths'] if 'python' in config else None,
            config['php_next']['paths'] if 'php_next' in config else None,
            config['node_next']['paths'] if 'node_next' in config else None
        ]

        for base_paths in base_paths_list:
            if base_paths is not None and _generate_plugin_path(plugin_name, base_paths):
                return _generate_plugin_path(plugin_name, base_paths)
        Log.error("Plugin name not found.")
        return False


def create_boilerplate(folder_path, boilerplate, data, extention,):
    """ to create boilerplate for a given path

    Args:
        folder_path (str): the destination path
        boilerplate (str): the name of the boilerplate
        data (dict): the data to be rendered
    """

    service_name = path.basename(folder_path)
    try:
        mkdir(folder_path)
    except OSError as err:
        Log.error(err)
        return

    dest_path = '{}/{}.{}'.format(
                folder_path, service_name, extention)

    render_boilerplate(boilerplate=boilerplate, data=data,
                       destination_path=dest_path)

    Log.info(
        'Plugin created at {}'.format(dest_path))


def show_schema(base_path):
    """ this method will show the schema of a plugin if it has schema.json

    Args:
        base_path (str): the base path of the plugin  eg: /home/vtx-services/aaa_com/
    """

    schema_path = base_path + '/schema.json'
    if path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                schema = f.read()
                schema = json.loads(schema)
                for page in schema.keys():
                    Log.standout(f"Schema for Page: {page}")
                    schema_heading = ['field', 'type', 'pattern']
                    table_data = [
                        schema_heading
                    ]

                    for th, td in schema[page]['schema']['properties'].items():
                        if 'pattern' in td:
                            row = [th, td['type'], td['pattern']]
                        else:
                            row = [th, td['type'], '']

                        table_data.append(row)

                    print(SingleTable(table_data).table)
                return True
        except:
            Log.warn("Schema Structured Incorrectly")
    else:
        Log.warn("Schema Not Found")
        return False

COMMENT_BLOCK_PATTERN = re.compile(r"(\/\*\*.?\n)(.*?)(\s*\*\/\s*\n)", re.DOTALL)
CLASS_DECLARATION_PATTERN = re.compile(r'class\s+\w+\s+extends\s(\w+)\b', re.DOTALL)

def user_input(msg, default='Y'):
    while True:
        choice = input(msg + ' [Y/n]: ' if default == 'Y' else ' [y/N]: ').upper()
        if choice == 'N':
            return 'N'
        elif choice == 'Y':
            return 'Y'
        elif choice == '':
            return default

def list_dependencies(plugin_name):
    """list dependencies by listing all base_class"""

    dependencies = set()
    while True:
        plugin_dir_path = get_plugin_path(plugin_name)
        if not plugin_dir_path:
            break
        plugin_path = path.join(plugin_dir_path, plugin_name + '.php')
        contents = read_text(plugin_path)
        match = CLASS_DECLARATION_PATTERN.search(contents)
        if not match:
            break
        base_class = match.group(1)
        if base_class == 'Vtx_Service_Plugin':
            break
        plugin_name = base_class
        dependencies.add(plugin_name)
    return list(dependencies)

def insert_all_chained_dependencies(plugin_name):
    """add dependencies if the dependencies follow service_code/service_code.php pattern, however deep"""

    dependencies = list_dependencies(plugin_name)
    plugin_dir_path = get_plugin_path(plugin_name)
    if not plugin_dir_path:
        return
    plugin_path = path.join(plugin_dir_path, plugin_name + '.php')
    contents = read_text(plugin_path)
    mappings = get_comment_block(contents)
    if 'Dependencies' not in mappings:
        mappings['Dependencies'] = ''
        original_deps = []
    else:
        original_deps = mappings['Dependencies'].split(',')
    
    mappings['Dependencies'] = ','.join(list(set(dependencies + original_deps)))
    contents = set_comment_block(contents, mappings)
    write_text(plugin_path, contents)
    return True

def set_comment_block(script, mappings):
    comment_block = ' * ' + '\n * '.join([f'{k}: {v}' for k, v in mappings.items()])
    subbed = COMMENT_BLOCK_PATTERN.sub('\\1' + comment_block + '\\3', script)
    return subbed

def get_comment_block(script):
    match = COMMENT_BLOCK_PATTERN.search(script)
    if not match:
        return {}
    doc = match.group(2)
    lines = doc.splitlines()
    mappings = {}
    for line in lines:
        splitted = line.lstrip(' *').split(':', 1)
        if len(splitted) != 2:
            continue
        k, v = splitted
        mappings[k.strip()] = v.strip()
    return mappings

def get_plugin_info(plugin_path):
    """ get plugin's info like service_name,pid,description from the plugin's base folder.
    It does so by reading the file and looking at the info from plugin which is commented
    at the beginning.

    Args:
        plugin_path (str): the path of the directory where we find the plugin.
    """
    plugin_file_path = listdir(plugin_path)

    files = [f for f in plugin_file_path]
    plugin_file = ''
    for file in files:
        if path.basename(plugin_path) in file:
            plugin_file = file
            break

    if plugin_file:
        try:
            with open(path.join(plugin_path, plugin_file)) as f:
                script = f.read()
                match = CLASS_DECLARATION_PATTERN.search(script)
                base_class = None
                if match:
                    base_class = match[1]

                # TODO: use tree-sitter to parse php file.
                mappings = {k.upper(): v for k, v in get_comment_block(script).items()}
                if not mappings:
                    return {}
                dependencies_str = mappings.get('DEPENDENCIES', '')
                dependencies = [d.strip() for d in dependencies_str.split(',')]
                pid_line = mappings.get('PID', '')
                ssv = pid_line.split(' ')
                pid = ssv[0].strip()

                pid_forced = False
                if len(ssv) > 1:
                    pid_forced = ssv[1].strip() == 'force'
                
                # TODO: to parse php import mechanisms like require_once, include_once, etc. for dependencies 
                return {
                    'pid': pid,
                    'pid_forced': pid_forced,
                    'report_name': mappings.get('NAME'),
                    'description': mappings.get('DESCRIPTION'),
                    'dependencies': dependencies,
                    'base_class': base_class
                }
        except KeyError as e:
            pass
    return {}

def render_boilerplate(boilerplate, data, destination_path):
    """parse boilerplate from template directory to start a project

    Args:
        boilerplate (str): name of boilerplate template
        data (dict): input for the boilerplate
        destination_path: the final path where the final content needs to be saved
    """

    template_dir = Path(__file__).parent.parent.absolute()
    template_file = '{}/templates/{}'.format(template_dir, boilerplate)
    with open(template_file) as file:
        template = Template(file.read())
        with open(destination_path, 'w') as dest_file:
            dest_file.write(template.render(data))


def _generate_plugin_path(plugin_name, paths):
    
    for service_path in paths:
        plugin_path = path.join(service_path, plugin_name)
        plugin_path = path.expanduser(plugin_path)
        if path.exists(plugin_path):
            return plugin_path
    return False


def get_docker_entrypoints(image_name):
    o = subprocess.run(f'docker inspect {image_name}', shell=True, capture_output=True, text=True)
    try:
        image_info = json.loads(o.stdout)
    except json.JSONDecodeError:
        raise Exception('Running docker inspect failed. Is SDK image correct?')
    try:
        return image_info[0]['Config']['Entrypoint']
    except IndexError:
        raise Exception('Docker inspect failed. Is Docker Running? Is SDK image available?')

def write_text(file_path, contents):
    "helper function to write text to file with compatible encoding and no newline magic"

    # turn off universal-newline mode for less surprises.
    with open(file_path, 'w', encoding='UTF-8', newline='') as fd:
        fd.write(contents)

def read_text(file_path):
    "helper function to read text from file with compatible encoding and no newline magic"

    # turn off universal-newline mode for less surprises.
    with open(file_path, 'r', encoding='UTF-8', newline='') as fd:
        contents = fd.read()

    return contents