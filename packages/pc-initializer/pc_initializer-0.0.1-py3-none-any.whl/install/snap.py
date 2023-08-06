from util.util import Util

class Snap:
    def install(self, conf, dry_run = True):
        packages = conf['packages']
        for package in packages:
            Util.execute(f'sudo snap install --classic {package}', dry_run)
            Util.execute(f'sudo snap refresh {package}', dry_run)