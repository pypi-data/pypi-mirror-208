import logging
import os
import json
import sys 
import subprocess
from distutils import util

class Util:
    tmp_path = os.path.expanduser(os.path.join('/tmp', 'linux-setup'))

    @staticmethod
    def read_json_file(file):
        data = {}
        with open(file) as f:
            data = json.load(f)

        return data

    @staticmethod
    def read_json(file, path, default = ''):
        value = Util.read_json_file(file)

        keys = path.split('.')
        for key in keys:
            if not key in value:
                return default

            value = value[key]

        return value

    @staticmethod
    def to_bool(value):
        return bool(util.strtobool(str(value)))

    @staticmethod
    def expand_path(path):
        return os.path.expanduser(path)

    @staticmethod
    def to_list(cmd):
        return cmd.split(' ')

    @staticmethod
    def create_dir(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    def execute(cmd, dry_run):
        if isinstance(cmd, str):
            cmd = Util.to_list(cmd)
        logging.info(f'Command: \"{" ".join(cmd)}\"')

        if dry_run:
            logging.warning(f'Skipped because dry run was set')
            return 'dry_run'

        res = subprocess.run(cmd)

        if res.returncode != 0:
            sys.exit(1)