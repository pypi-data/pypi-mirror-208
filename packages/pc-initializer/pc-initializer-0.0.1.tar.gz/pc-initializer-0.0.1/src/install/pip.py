from util.util import Util

class Pip:
    def install(self, conf, dry_run = True):
        packages = conf['packages']
        Util.execute('python3 -m pip install {}'.format(' '.join(packages)), dry_run)