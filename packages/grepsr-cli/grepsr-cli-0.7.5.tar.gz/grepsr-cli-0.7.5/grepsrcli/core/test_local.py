from os import path, system
import json
import subprocess
from .message_log import Log
from .config import load_config, config_path as CONFIG_PATH
from .utils import get_docker_entrypoints, write_text, read_text

class TestLocal:
    def __init__(self, type, base_path, plugin_name, params=None, params_file=None, is_multi_proc=False):
        self.type = type
        self.plugin_name = plugin_name
        self.base_path = base_path

        self.tmp_path = path.expanduser('~') + '/.grepsr/tmp/'
        self.config = load_config('config.yml')
        self.type_config = self.config[type]
        self.params = params
        self.params_file = params_file
        self.is_multi_proc = is_multi_proc
        self.test_script()

    def test_script(self):
        if self.type == "php":
            if "env" in self.type_config:
                if self.type_config['env']:
                    self.test_script_php(env=True)
                else:
                    self.test_script_php(env=False)
            else:
                self.test_script_php(env=False)
        elif self.type == "php_next":
            self.test_script_php_next()

    def test_script_php(self, env=False):
        if self.is_multi_proc is None:
            # only use the value of multiprocess if it is not passed explicitly from cmd line
            try:
                self.is_multi_proc = 1 if self.type_config['multiprocess'] == True else 0
            except KeyError:
                pass
        env_vars = []
        if env:
            env_vars = [
                f'-e {env_var}={self.type_config["env"][env_var]}' for env_var in self.type_config["env"].keys()
            ]
        sdk_args_list = [
            f'-s {self.plugin_name}',
        ]
        if self.is_multi_proc is not None:
            sdk_args_list.append(f'-m {self.is_multi_proc}')
        docker_image_name = self.type_config["sdk_image"]
        json_content = self.params
        pre_entrypoint = self.type_config.get('pre_entry_run_file')
        only_service = (not self.params) and (not self.params_file) and (not pre_entrypoint)
        bash_cmd = ''
        if only_service:
            sdk_args = ' '.join(sdk_args_list)
        else:
            if self.params_file:
                # should be able to pass any path, not limited to just tmp/
                fp = path.expandvars(path.expanduser((self.params_file)))
                if not path.isabs(fp):
                    fp = path.join(self.tmp_path, fp)
                with open(fp, 'r', encoding='UTF-8') as fd:
                    json_content = fd.read()

            pipe_params = ''
            sh_contents = ['#!/bin/bash']
            if json_content:
                sdk_args_list.append("-p")

                # json decode and encode is required to remove spaces from the passed params
                # because the bash shell file that forwards argument is not quoted ($@)
                # which causes it to treat spaces anywhere as being a different argv
                params_decoded = json.loads(json_content)
                compact_json = json.dumps({'params': params_decoded}, separators=[',', ':'])
                # now that all non important spaces are removed, replace spaces
                # inside (keys and) values with unicode code-point which is luckily accepted by shell.
                # hack: if the shell cannot handle space char, sneak the space with a makeup.
                compact_json = compact_json.replace(' ', '\\u0020')
                
                tmp_json_file = '_gcli_internal_params_tmp.json'
                # write the compacted json, to tmp/ directory whcih will get mounted 
                # to docker container. Params are written to temporary file and not passed
                # in the shell due to quoting issues.
                write_text(path.join(self.tmp_path, tmp_json_file), compact_json)
                pipe_params = f"$(</tmp/{tmp_json_file})"
                
            
            custom_shell_file = '_gcli_internal_shell_file.sh'
            custom_shell_file_local = path.join(self.tmp_path, custom_shell_file)
            
            if pre_entrypoint:
                sh_contents.append(read_text(path.join(self.tmp_path, pre_entrypoint)))
                
            sdk_args = ' '.join(sdk_args_list)
            original_entrypoints = get_docker_entrypoints(image_name=docker_image_name)
            sh_contents.append(f'source {original_entrypoints[0]} {sdk_args} {pipe_params}')
            write_text(custom_shell_file_local, '\n'.join(sh_contents))

            bash_cmd = f'source /tmp/{custom_shell_file}'

        commands = [
                'docker run -t -i --network="host" --rm',
                f'-v {self.base_path}:/home/grepsr/vortex-plugins/{path.basename(self.base_path)}',
                f'-v {self.tmp_path}:/tmp',
                f'-e APP_ENV={self.config["app_env"]}',
                " ".join(env_vars),
                f'--entrypoint=""' if not only_service else '',
                docker_image_name,
                f'bash -ci "{bash_cmd}"' if not only_service else sdk_args,
        ]

        command = ' '.join([command for command in commands if command])
        # print(command, flush=True)
        system(command)

    def test_script_php_next(self):

        command = f'''docker run -t -i --network="host" --rm \
                     -v {self.base_path}:/home/grepsr/vortex-backend-next/scraper-plugins \
                     -v {self.tmp_path}:/tmp \
                     -e APP_ENV={self.config['app_env']} \
                     {self.type_config['sdk_image']} -s {self.plugin_name} '''
        system(command)

    def test_script_local(self):
        pass
