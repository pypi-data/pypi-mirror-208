import logging

from util.util import Util

class Flatpak:
    def install(self, conf, dry_run = True):
        remotes = conf['remotes']
        packages = conf['packages']

        for remote in remotes:
            logging.info(f"Adding flatpak remote {remote}")
            Util.execute(f'flatpak remote-add --if-not-exists -v {remote}', dry_run)

        Util.execute(f'flatpak install -y  {" ".join(packages)}', dry_run)
