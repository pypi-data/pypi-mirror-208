import os

from util.util import Util

class ConfigReader:
    @staticmethod
    def get(args, path = None):
        if not path:
            path = args.SUBCOMMAND.lower()

        setup_file = os.path.expanduser(args.setup_file)
        config = Util.read_json(setup_file, path, {})
        defaults = Util.read_json(setup_file, 'defaults', {})

        for key in defaults:
            if key not in config:
                config[key] = defaults[key]

        ConfigReader.add_cmd_argument(config, args, 'github_repo')
        ConfigReader.add_cmd_argument(config, args, 'github_token')

        ConfigReader.add_boolean_cmd_argument(config, args, 'local')
        ConfigReader.add_cmd_argument(config, args, 'path')

        ConfigReader.add_cmd_argument(config, args, 'config_file')
        ConfigReader.add_cmd_argument(config, args, 'output_dir')
        ConfigReader.add_boolean_cmd_argument(config, args, 'dry_run')
        ConfigReader.add_boolean_cmd_argument(config, args, 'recreate')
        ConfigReader.add_boolean_cmd_argument(config, args, 'subdir')

        if 'config-file' not in config:
            config['config-file'] = f'{args.SUBCOMMAND}.json'

        return config

    @staticmethod
    def add_cmd_argument(config, args, name):
        json_name = name.replace('_', '-')
        if name in args:
            value = getattr(args, name)
            if value != '':
                config[json_name] = value

    @staticmethod
    def add_boolean_cmd_argument(config, args, name):
        json_name = name.replace('_', '-')
        if name in args:
            is_set = getattr(args, name)
            if is_set:
                config[json_name] = True

        name = f'disable_{name}'
        if name in args:
            is_set = getattr(args, name)
            if is_set:
                config[json_name] = False
