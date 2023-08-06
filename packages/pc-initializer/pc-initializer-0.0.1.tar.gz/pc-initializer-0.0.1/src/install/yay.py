from util.util import Util

class Yay:
    def install(self, conf, dry_run = True):
        packages = conf['packages']
        Util.execute('yay -Sy --needed --noconfirm {}'.format(' '.join(packages)), dry_run)