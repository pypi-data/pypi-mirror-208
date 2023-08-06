from util.util import Util

class Apt:
    def install(self, conf, dry_run = True):
        packages = conf['packages']
        Util.execute('sudo apt install -y {}'.format(' '.join(packages)), dry_run)