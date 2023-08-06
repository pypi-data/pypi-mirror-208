import argparse
import os

import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

from install.install import Install
from util.util import Util
from i3.i3_config import I3Config
from env import Env
from venv_helper import VenvHelper
from devtools import Devtools

def execute_subcommand(args):
    dirs = ['config_dir', 'output_dir']

    for dir in dirs:
        if dir in vars(args):
            setattr(args, dir, os.path.expanduser(getattr(args, dir)))

    switcher = {
        "devtools": Devtools.download_devtools,
        "env": Env.create_config,
        "i3": I3Config.create_config,
        "install": Install.install,
        "venv": VenvHelper.create_venv
    }

    switcher.get(args.SUBCOMMAND, lambda args: print(f"Subcommand '{args.SUBCOMMAND}' not implemented"))(args)


def main():
    def add_boolean_pair(parser, short_flag, name):
        parser.add_argument(f'-d{short_flag}', f'--disable-{name}', help='no_dry_run', default=False, action='store_true')
        parser.add_argument(f'-{short_flag}', f'--{name}', help='dry_run', default=False, action='store_true')

    def add_output_dir(parser):
        parser.add_argument('-o', '--output-dir', metavar='output_dir', help='specify output_dir', default='')
        add_boolean_pair(parser, 's', 'subdir')

        # parser.add_argument('-s', '--create-subdir', help='create_subdir', default=False, action='store_true')

    def add_config_file(parser):
        parser.add_argument('-gr', '--github-repo', metavar='github_repo', help='specify github_repo', default='')
        parser.add_argument('-gt', '--github-token', metavar='github_token', help='specify github_token', default='')
        # parser.add_argument('-l', '--local', help='local', default=False, action='store_true')
        add_boolean_pair(parser, 'l', 'local')

        parser.add_argument('-p', '--path', metavar='path', help='specify path', default='')

        parser.add_argument('-cf', '--config-file', metavar='config_file', help='specify config_file', default='')

    def add_dryrun(parser):
        add_boolean_pair(parser, 'dr', 'dry-run')
        # parser.add_argument('--no-dry-run', help='no_dry_run', default=False, action='store_true')
        # parser.add_argument('--dry-run', help='dry_run', default=False, action='store_true')
        
    parser = argparse.ArgumentParser(description='Linux setup')
    parser.set_defaults(handler=execute_subcommand)
    parser.add_argument('-s', '--setup-file', metavar='setup_file', help='specify setup_file', default='~/.initializer')

    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'SUBCOMMAND'

    parser_i3 = subparsers.add_parser('i3', help='Create i3 config')
    add_dryrun(parser_i3)
    add_config_file(parser_i3)

    parser_env = subparsers.add_parser('env', help='Create env')
    add_dryrun(parser_env)
    add_config_file(parser_env)
    add_output_dir(parser_env)

    parser_devtools = subparsers.add_parser('devtools', help='Download devtools')
    add_dryrun(parser_devtools)
    add_config_file(parser_devtools)
    add_output_dir(parser_devtools)

    parser_install = subparsers.add_parser('install', help='Install packages')
    add_dryrun(parser_install)
    add_config_file(parser_install)
    # parser_install.add_argument('-i', '--config-file', metavar='install_file', help='specify install_file', default='install.json')
    # parser_install.add_argument('-a', '--all', help='all', action='store_true')
    parser_install.add_argument('-pm', '--package-managers', metavar='package_managers', help='specify package_managers to install', default='')
    # parser_install.add_argument('-y', '--yay', help='yay', action='store_true')
    # parser_install.add_argument('--pip', help='pip', action='store_true')
    # parser_install.add_argument('-s', '--snap', help='snap', action='store_true')
    # parser_install.add_argument('-f', '--flatpak', help='flatpak', action='store_true')

    parser_venv = subparsers.add_parser('venv', help='Create venv')
    add_dryrun(parser_venv)
    add_output_dir(parser_venv)
    add_boolean_pair(parser_venv, 'f', 'recreate')

    args = parser.parse_args()

    ret = args.handler(args)

if __name__ == "__main__":
    main()
