import os
import logging

from util.config_reader import ConfigReader
from util.github_repo import GithubRepo
from util.util import Util

class Env:
    @staticmethod
    def create_config(args):
        config = ConfigReader.get(args)

        gr = GithubRepo(args)
        data = gr.get_json(config['config-file'])

        output_dir = config['output-dir']
        if config['subdir']:
            output_dir = os.path.join(output_dir, 'env')
        dry_run = config['dry-run']

        env_file_name = os.path.join(output_dir, "env.sh")

        shell = data.get('shell', 'zsh')

        content = []
        content.append(f'#!/bin/{shell}')
        content.append('')

        get_script_dir = ''
        match shell:
            case 'bash':
                get_script_dir = '$(dirname "${BASH_SOURCE[0]}")'
            case 'zsh':
                get_script_dir = '${0:a:h}'
            case _:
                raise Exception(f'Shell {shell} is currently not supported')
        content.append(f'export ENV_FOLDER="{get_script_dir}"')
        content.append('')

        for env_var in data.get("env", {}).items():
            content.append(f'export {env_var[0]}={env_var[1]}')
        content.append('')

        for p in data.get("path", []):
            content.append(f'export PATH={p}:$PATH')
        content.append('')

        for alias in data.get("alias", {}).items():
            content.append(f'alias {alias[0]}=\"{alias[1]}\"')
        content.append('')

        for source in data.get("source"):
            content.append(f'if [ -f "{source}" ]; then')
            content.append(f'  source {source}')
            content.append('fi')
            content.append('')

        content = '\n'.join(content)

        rc_file = os.path.expanduser(f'~/.{shell}rc')

        source_env_file = f'source {env_file_name}'

        source_env = ['']
        source_env.append(f'if [ -f "{env_file_name}" ]; then')
        source_env.append(f'\t{source_env_file}')
        source_env.append('fi')
        source_env.append('')
        rc_content = '\n'.join(source_env)

        add_to_rc_file = False
        with open(rc_file) as f:
            add_to_rc_file = not source_env_file in f.read()


        if dry_run:
            print("Create {} with content:".format(env_file_name))
            print(content)
            if add_to_rc_file:
                print(f'Would add script to rc file {rc_file}')
                print(rc_content)
            else:
                print(f'{rc_file} already loads env file')
        else:
            logging.info(f'Used output_dir {output_dir}')
            Util.create_dir(output_dir)
            with open(env_file_name, "w+") as file:
                file.write(content)

            if add_to_rc_file:
                with open(rc_file, 'a') as f:
                    f.write(rc_content)

            logging.info(f'Created {env_file_name}')

        # TODO Create env_devtools.sh, env_venv.sh and env_custom.sh