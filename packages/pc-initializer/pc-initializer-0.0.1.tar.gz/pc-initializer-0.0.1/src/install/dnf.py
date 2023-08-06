from util.util import Util

class Dnf:
    def install(self, conf, dry_run = True):
        if 'remotes' in conf:
            remotes = conf['remotes']

            for remote in remotes:
                base_url = remote['baseurl']
                gpgkey = remote['gpgkey']

                Util.execute(f'sudo rpm --import {gpgkey}', dry_run)
                Util.execute(f'sudo dnf config-manager --add-repo {base_url}', dry_run)

        packages = conf['packages']
        print(f'Install {packages}')
        Util.execute('sudo dnf install -y {}'.format(' '.join(packages)), dry_run)
