from os import system, path
import os
import sys
import subprocess
import multiprocessing
import signal
import json
import pathlib
from semver import VersionInfo
from cement import Controller, ex
from ..core.config import load_config
from ..core.utils import (
    create_boilerplate,
    render_boilerplate,
    get_plugin_info,
    get_plugin_path,
    show_schema,
    user_input,
    insert_all_chained_dependencies
)
from ..core.test_local import TestLocal
from ..core.message_log import Log
from ..core.aws_s3 import S3

class CrawlerBase(Controller):
    class Meta:
        label = 'crawler_base'


class Crawler(Controller):
    config = load_config('config.yml')

    class Meta:
        label = 'crawler'
        stacked_on = 'crawler_base'
        stacked_type = 'nested'

    @ex(
        help="test a plugin locally",
        aliases=['tst'],
        arguments=[
            (['-s'], {
                'action': 'store',
                'dest': 'plugin_name',
                'help': "The name of the service/plugin to run locally"
            }),
            (['-p'], {
                'action': 'store',
                'dest': 'params',
                'help': 'Parameters (as JSON) to pass to the arguments of the main function',
            }),
            (['-m'], {
                'action': 'store',
                'dest': 'multi_proc_mode',
                'help': 'Multiprocess mode',
            }),
            (['--params-file'], {
                'action': 'store',
                'dest': 'params_file',
                'help': 'JSON file location containing parameters to pass to the arguments of the main function'
            }),
            
        ]
    )
    def test(self):
        plugin_name = self.app.pargs.plugin_name
        main_fn_params = self.app.pargs.params
        main_fn_params_file = self.app.pargs.params_file
        is_multi_proc = self.app.pargs.multi_proc_mode

        platforms = ['php', 'php_next']
        proc = None
        for platform in platforms:
            if platform in self.config:
                plugin_path = get_plugin_path(plugin_name, type=platform)
                if plugin_path:
                    base_path = pathlib.Path(get_plugin_path(plugin_name, type=platform)).parent
                    if is_multi_proc == '1':
                        from ..core import multiproc_server
                        proc = multiprocessing.Process(target=multiproc_server.start, args=[])
                        proc.start()
                    try:
                        TestLocal(type=platform, base_path=base_path, plugin_name=plugin_name, params=main_fn_params, params_file=main_fn_params_file, is_multi_proc=is_multi_proc)
                    except json.JSONDecodeError as e:
                        self.app.log.error(f"Error decoding params as JSON. {e}")
                        self.app.exit_code = 10
                    except FileNotFoundError as e:
                        self.app.log.error(f"Params file: `{main_fn_params_file}` not found. {e}")
                        self.app.exit_code = 20
                    break
        else:
            self.app.log.error(f"path: {plugin_name} not found!")
            self.app.exit_code = 127
        if proc:
            print('terminating server proc', flush=True)

            '''these 2 methods cannot kill the currently running process on linux.
            Although they will raise an Exception on the target server process,
            the child process of that script cannot be terminated from it.
            '''
            # proc.terminate()
            # proc.kill()
            
            '''instead killing whole process group works on linux.
            The OS handles this, killing all the processes at once.
            '''
            pgid = os.getpgid(os.getpid())
            if pgid == 1:
                os.kill(os.getpid(), signal.SIGINT)
            else:
                os.killpg(os.getpgid(os.getpid()), signal.SIGINT)


    @ex(
        help="performs git pull to update the codebase",
        arguments=[
            (['-t', '--type'], {
                'action': 'store',
                'dest': 'type',
                'help': "Platform type: php|node|python|php_next"
            })
        ]
    )
    def sync(self):
        if(self.app.pargs.type):
            type = self.app.pargs.type
            crawler_paths = self.config[type]['paths']

            for crawler_path in crawler_paths:
                Log.info(f"Syncing: {crawler_path}")
                system(
                    f"""cd {crawler_path}  && git pull origin master""")
        else:
            Log.warn("Please enter a valid type")

    @ex(
        help="create basic boilerplate for plugins ",
        arguments=[
            (['-s'], {
                "action": "store",
                "dest": "plugin_name",
                "help": "the name of the plugin to be created"
            }), (['-pid'], {
                "action": "store",
                "dest": 'pid',
                "help": "the project id of the plugin"
            }), (
                ['-t', '--template'], {
                    "action": "store",
                    "dest": 'template',
                    "help": "choose a template to boilerplate php|node|py|vc defaults to php"
                }
            ), (
                ['--path'], {
                    'action': "store",
                    'dest': 'folder_path',
                    'help': 'the path of the folder where the plugin will reside'
                }
            )
        ]
    )
    def create(self):

        template = self.app.pargs.template

        if self.app.pargs.folder_path is not None:
            folder_path = self.app.pargs.folder_path
            folder_path = folder_path.rstrip('/')
            folder_path = path.expanduser(folder_path)
        else:
            folder_path = pathlib.Path().resolve()
            folder_path = str(folder_path)

        if self.app.pargs.plugin_name is not None:
            plugin_name = self.app.pargs.plugin_name
        else:
            self.app.log.error(
                "cannot create boilerplate file without plugin's name")
            return

        if self.app.pargs.pid is not None:
            pid = self.app.pargs.pid
        else:
            pid = '***'

        data = {
            'plugin_name': plugin_name,
            'pid': pid
        }
        plugin_path = folder_path + '/' + plugin_name
        if template == 'vc':
            create_boilerplate(
                plugin_path, "php_vc_boilerplate.jinja2", data, 'php')

        elif template == 'py':
            create_boilerplate(
                plugin_path, "py_boilerplate.jinja2", data, 'py')

        elif template == 'node':
            create_boilerplate(
                plugin_path, "node_boilerplate.jinja2", data, 'js')
        elif template == 'brp':
            create_boilerplate(
                plugin_path, "php_brp_boilerplate.jinja2", data, 'php')
        else:
            create_boilerplate(
                plugin_path, "php_boilerplate.jinja2", data, 'php')

    @ex(
        help="deploy a specific plugin to live with versioning",
        arguments=[
            (['-s'], {
                "action": "store",
                "dest": 'plugin_name'
            }), (['-m'], {
                "action": "store",
                "dest": "message"
            }), (['-st', '--stable'], {
                "action": "store_true",
                "dest": "stable_flag"
            }), (['--patch'], {
                "action": "store_true",
                "dest": "patch_flag"
            }), (['--minor'], {
                "action": "store_true",
                "dest": "minor_flag",
                "help": "set major of a version"
            }), (['--major'], {
                "action": "store_true",
                "dest": "major_flag"
            }),
            (['--verbose'], {
                "action": 'store_true',
                "dest": "verbose"
            })
        ]
    )
    def deploy(self):

        toolbar_width = 50
        verbose_mode = False

        try:
            if self.config['deploy']['verbose'] == True or self.app.pargs.verbose == True:
                verbose_mode = True
        except:
            if self.app.pargs.verbose == True:
                verbose_mode = True

        input_plugin_name = self.app.pargs.plugin_name
        deploy_message = self.app.pargs.message

        if input_plugin_name is None:
            self.app.log.error("cannot deploy without service code")
            return False
        if deploy_message is None:
            self.app.log.error("cannot deploy without deploy message")
            return False

        if self.app.pargs.stable_flag:
            deploy_type = "DEPLOY-STABLE"
        else:
            deploy_type = "DEPLOY"

        major_flag = self.app.pargs.major_flag
        minor_flag = self.app.pargs.minor_flag

        plugin_names = False
        if ',' in input_plugin_name:
            plugin_names = input_plugin_name.split(',')

        if plugin_names == False:
            plugin_names = []
            plugin_names.append(input_plugin_name)

        for plugin_name in plugin_names:
            plugin_name = plugin_name.strip()
            plugin_dir_path = get_plugin_path(plugin_name, all_types=True)

            if not plugin_dir_path:
                self.app.log.error(f'Could not find plugin: {plugin_name}')
                continue

            plugin_info = get_plugin_info(plugin_dir_path)
            if plugin_info:
                base_class = plugin_info['base_class']
                if base_class != 'Vtx_Service_Plugin':
                    if base_class not in plugin_info['dependencies']:
                        msg = f'Plugin extends {base_class} but does not declare it as a dependency.'
                        self.app.log.warning(msg)
                        if user_input(f'[Experimental] Do you want to automatically add dependencies?') == 'Y':
                            insert_all_chained_dependencies(plugin_name)
                        go_fwd = user_input(f'Do you want to continue?')
                        if go_fwd == 'N':
                            continue
            # add .version or update .version
            version_path = '{}/.version'.format(plugin_dir_path)
            if path.exists(version_path):
                with open(version_path, 'r') as f:
                    version_info = VersionInfo.parse(f.read())
                    if(major_flag):
                        version_info = version_info.next_version(
                            part='major')
                    elif(minor_flag):
                        version_info = version_info.next_version(
                            part='minor')
                    else:
                        version_info = version_info.bump_patch()

                    version_info = str(version_info)
                    with open(version_path, 'w') as w:
                        w.write(version_info)

                self.app.log.info(
                    "[{}] [{}] {}".format(deploy_type, version_info, deploy_message))
            else:
                if plugin_info:
                    # if its already deployed then the service probabily works fine.
                    # if its the first deploy, we annoy the user.
                    if not plugin_info.get('pid_forced'):
                        # TODO: maybe read all files and check if any service already has pid in which case force ought to be required.
                        self.app.log.warning("PID was not forced. This may cause issues.")

                with open(version_path, 'w') as f:
                    if major_flag:
                        version_info = "1.0.0"
                    elif minor_flag:
                        version_info = "0.1.0"
                    else:
                        version_info = "0.0.1"

                    f.write(version_info)

                self.app.log.info(
                    "[{}] [{}] {}".format(deploy_type, version_info, deploy_message))

            if verbose_mode is False:
                sys.stdout.write(
                    "Deploying: [%s]" % (" " * toolbar_width))
                sys.stdout.write("\b" * (toolbar_width + 1))
                sys.stdout.flush()
            try:
                quiet_mode = "" if verbose_mode else "--quiet"
                cd_to_repo_cmd = f"cd {plugin_dir_path} && cd .."
                # dont pop stash. cuz if there is a merge conflict, good luck with that.
                # instead apply stash and if and only if everything has passed, then drop the stash.
                # TODO: only apply stash if git stash stashed > 0 files.
                cmds = [
                    cd_to_repo_cmd,
                    f'git stash --include-untracked {quiet_mode}',
                    f'git pull origin master {quiet_mode}',
                    f'git stash apply {quiet_mode}',
                    f'git add {plugin_name}/',
                    f'git commit -m "[{deploy_type}] [{version_info}] {deploy_message}" {quiet_mode}',
                    f'git push origin master {quiet_mode}',
                ]
                post_deploy_cmds = [
                    cd_to_repo_cmd,
                    f'git stash drop {quiet_mode}'
                ]
                try:
                    multiplier = toolbar_width // len(cmds)
                except ZeroDivisionError:
                    multiplier = 0
                if verbose_mode:
                    multiplier = 0
                # just echo some dashes after each command for progress. lol.
                echoer = 'echo -n ' + '-' * multiplier
                # .join() only does n-1 additions. Hence add a echoer at last. And then echo remaining to fill the bar (caused by floor division)
                cmd = f' && {echoer} &&'.join(cmds) + f' && {echoer}' + f' && echo -n {"-" * (toolbar_width - (len(cmds) * multiplier))}'
                try:
                    proc = subprocess.run(cmd, shell=True, check=True, timeout=300)
                    if proc.returncode == 0:
                        proc = subprocess.run(' && '.join(post_deploy_cmds), shell=True)
                        if proc.returncode != 0:
                            self.app.log.warning('Failed to drop the latest stash.')

                except subprocess.TimeoutExpired:
                    self.app.log.error(f'Timeout occured when deploying {plugin_name}')

            except subprocess.CalledProcessError as e:
                self.app.log.error(f'There was a problem deploying {plugin_name}')

                return

            if verbose_mode is False:
                sys.stdout.flush()
                sys.stdout.write("\n")

            show_schema(plugin_dir_path)

            try:
                app_url = f'https://platform.grepsr.com/projects/{plugin_info["pid"]}'
                self.app.log.info(f"App Url: {app_url}")
            except KeyError:
                self.app.log.warning(f"Cannot find pid in plugin, please find the project's url manually")

            self.app.log.info(
                f"Plugin: {plugin_name} deployed successfully")

    @ex(
        help="use a base plugin from: https://bitbucket.org/grepsr/vortex-plugins-services-base",
        arguments=[
            (['-s'], {
                "help": "name of the base crawler you want to use",
                "action": "store",
                "dest": "base_plugin_name"
            }),
            (['-t'], {
                "help": "name of target crawler that you want to use",
                "action": "store",
                "dest": "plugin_name"
            })
        ]
    )
    def use_basecrawler(self):

        s3 = S3(aws_id=self.config['aws_access_key_id'],
                aws_sec_key=self.config['aws_secret_access_key'])

        version = None
        base_plugin_name = self.app.pargs.base_plugin_name
        target_plugin_name = self.app.pargs.plugin_name

        if(base_plugin_name is None or target_plugin_name is None):
            Log.error(
                "Please Enter base crawler and target cralwers.\nUse gcli crawler use-basecrawler -h for more information")
            return

        if('-' in base_plugin_name):
            version = base_plugin_name.split('-')[1]
            base_plugin_name = base_plugin_name.split('-')[0]

        # to check if there is a base-plugin in thier gcli settings ...
        base_plugin_dir_path = get_plugin_path(
            base_plugin_name, type='php')

        target_plugin_path = get_plugin_path(
            target_plugin_name, type='php'
        )

        if(version is None and base_plugin_dir_path):
            f = open(f"{base_plugin_dir_path}/.version", mode='r')
            version = f.read()
            f.close()

        if(version is None):
            Log.error(
                "Please Specify the version of base crawler that you want to use")
            return

        if(target_plugin_path):
            Log.info(
                f'Getting Secure Url of target plugin: {base_plugin_name}, {version}')

            presigned_url = s3.get_secure_url(bucket='crawler-plugins',
                                              filename=f'php/vortex-plugins-services-base/{base_plugin_name}/{base_plugin_name}-{version}.tar.gz')

            data = {
                'presigned_url': presigned_url,
                'plugin_name': base_plugin_name,
                'version': version
            }

            render_boilerplate(boilerplate='composer.jinja2', data=data,
                               destination_path=target_plugin_path + '/composer.json')
            system(
                f""" cd {target_plugin_path} &&  composer install""")
        else:
            Log.error(f"Target plugin: {target_plugin_name} not found")


    @ex(
        help="start multiprocess facilitation server",
        arguments=[]
    )
    def multiprocess(self):
        from ..core import multiproc_server
        multiproc_server.start()
        