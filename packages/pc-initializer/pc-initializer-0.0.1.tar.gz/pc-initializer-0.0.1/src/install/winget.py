from util.util import Util

class WinGet:
    def install(self, conf, dry_run = True):
        print(conf)
        for package in conf.get('packages', []):
            Util.execute(f'winget install --id={package} -e', dry_run)