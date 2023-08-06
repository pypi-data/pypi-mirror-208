import os
import shutil
import logging

from util.config_reader import ConfigReader
from util.github_repo import GithubRepo
from util.util import Util

class VenvHelper:
    @staticmethod
    def create_venv(args):
        config = ConfigReader.get(args)

        force = config.get('recreate', False)
        dry_run = config['dry-run']

        venv_dir = config['output-dir']
        if config['subdir']:
            venv_dir = os.path.join(venv_dir, 'venv')
        
        venv_exists = os.path.isdir(venv_dir)

        if not venv_exists or force:
            if venv_exists and not dry_run:
                logging.info(f"Remove old venv")
                shutil.rmtree(venv_dir)
            
            logging.info(f"Create venv {venv_dir}")
            Util.execute(f'python3 -m venv {venv_dir}', dry_run)
        else:
            logging.info(f"Venv {venv_dir} already exists")
            logging.info(f"To create a new venv use '--recreate'")

        env_output_dir = os.environ['ENV_FOLDER'] if 'ENV_FOLDER' in os.environ else output_dir
        env_file = os.path.join(env_output_dir, "env_venv.sh")
        content = f'source {venv_dir}/bin/activate'

        if dry_run:
            logging.info(f'Dry run active. Would create env file at {env_file}')
            print(content)
        else:
            logging.info(f'Create env file at {env_file}')
            Util.create_dir(env_output_dir)
            with open(env_file, "w+") as file:
                file.write(content)