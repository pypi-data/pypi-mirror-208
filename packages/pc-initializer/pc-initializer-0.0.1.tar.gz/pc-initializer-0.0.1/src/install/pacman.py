from util.util import Util

class Pacman:
    def install(self, conf, dry_run = True):
        packages = conf['packages']
        Util.execute('sudo pacman -Syu --noconfirm --needed {}'.format(' '.join(packages)), dry_run)