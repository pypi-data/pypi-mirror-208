
import sys
import argparse
import subprocess
import logging

from install.system_package_manager import SystemPackageManager
from install.flatpak import Flatpak
from install.yay import Yay
from install.pip import Pip
from install.snap import Snap

from util.config_reader import ConfigReader
from util.github_repo import GithubRepo
from util.util import Util

from util.os import OS, OSDetector

class Install:
    @staticmethod
    def install(args):
        system_package_manager = SystemPackageManager()
        switcher = {
            "system": SystemPackageManager(),
            "yay": Yay(),
            "pip": Pip(),
            "snap": Snap(),
            "flatpak": Flatpak()
        }

        config = ConfigReader.get(args)

        gr = GithubRepo(args)
        data = gr.get_json(config['config-file'])
        dry_run = config['dry-run']

        package_managers = config.get('package-managers', ['all'])

        if 'all' in package_managers:
            package_managers = list(switcher.keys())

        if not OSDetector.getOs() is OS.WINDOWS:
            if not dry_run:
                system_package_manager.install({'packages':['glibc']}, dry_run)

        for package_manager in package_managers:
            manager = switcher.get(package_manager, None)

            if manager:
                logging.info(f'Install {package_manager} packages')

                package_manager_conf = data.get(package_manager, None)
                
                if package_manager_conf:
                    manager.install(package_manager_conf, dry_run)
                else:
                    logging.warn(f'No conf for {package_manager}')
            else:
                logging.warn(f"Package manager '{package_manager}' not implemented, currently supported managers are {list(switcher.keys())}")
