import shutil
import sys
import os
import logging

from util.config_reader import ConfigReader
from util.github_repo import GithubRepo
from util.util import Util

from i3.cmd import ExecCmd, Cmd
from i3.wsp import Workspace
from i3.set import SetFromResource
from i3.key import Key
from i3.for_windows import ForWindows
from i3.mode import Mode
from i3.bar import Bar

class I3Config:
    @staticmethod
    def create_config(args):
        i3_config = I3Config()
        i3_config.create(args)

    def __init__(self):
        self.config = []
        self.keymap = []


    def create(self, args):
        config = ConfigReader.get(args)

        gr = GithubRepo(args)
        data = gr.get_json(config['config-file'])

        # config_dir = args.config_dir
        dry_run = config['dry-run']

        output_dir = Util.tmp_path if dry_run else os.path.expanduser(os.path.join('~', '.config'))
        i3_dir = f'{output_dir}/i3'

        i3_keymap = f'{i3_dir}/keymap'

        # logging.info(f'Used config_dir {config_dir}')
        logging.info(f'Used output_dir {output_dir}')
        logging.info(f'Used i3_dir {i3_dir}')


        def header(name):
            return f'#----------------{name}--------------------'

        # config_dir = os.environ["LINUX_SETUP_output_dir"]
        # data = Util.read_json_file(f"{config_dir}/i3-conf.json")

        Util.create_dir(i3_dir)

        self.append_string(
            config = f"set $mod {data['mod_key']}",
            keymap = f"$mod = {data['mod_key']}"
        )

        self.append_string()

        self.append_string_same(header('Workspaces'))

        for workspace in data['wsp']:
            wsp = Workspace(**workspace)
            for binding in wsp.getKeys():
                self.append_key(binding)

            for app in wsp.getAssignCmds():
                self.append_string_config(app)
        self.append_string_same('')

        if 'workspace_layout' in data:
            self.append_string_same(header('workspace_layout'))
            self.append_string_config(f"workspace_layout {data['workspace_layout']}")
            self.append_string_config()

        self.append_string_config(header('Autostart'))
        autostarts = data['autostart']

        self.append_string_config(header('init'))
        for init in autostarts['init']:
            self.append_string_config(ExecCmd(**init).getCmd())
        self.append_string_config('')

        self.append_string_config(header('always'))
        for always in autostarts['always']:
            always['always'] = True
            self.append_string_config(ExecCmd(**always).getCmd())
        self.append_string_config('')

        self.append_string_config(header('for_windows'))
        for window in data['for_windows']:
            self.append_string_config(ForWindows(**window).getCommand())
        self.append_string_config('')

        self.append_string_config(header('resources'))
        for resource in data['resources']:
            self.append_string_config(SetFromResource(**resource).get())
        self.append_string_config('')

        self.append_string_config(header('statements'))
        for statement in data['statements']:
            self.append_string_config(f"{statement}")
        self.append_string_config('')

        self.append_string_same(header('window'))
        for direction in data['direction']:
            for k in data['direction'][direction]:
                bind = {
                    "key": k,
                    "cmd": {
                        "cmd": f'focus {direction}'
                    },
                    "desc": f'Focus {direction} window'
                }
                self.append_key(Key(**bind))

                bind = {
                    "modifier": ['Shift'],
                    "key": k,
                    "cmd": {
                        "cmd": f'move {direction}'
                    },
                    "desc": f'Move focused window {direction}'
                }
                self.append_key(Key(**bind))

        self.append_string_same('')
            
        self.append_string_same(header('key-bindings'))
        for category in data['key-bindings']:
            self.append_string_same(header(category))
            for bind in data['key-bindings'][category]:
                self.append_key(Key(**bind))
            self.append_string_same('')
            
        self.append_string_same(header('mode'))
        self.append_string_same('')

        for name in data['mode']:
            self.append_string_same(header(name))
            modeDict = data['mode'][name]
            if "direction_options" in modeDict:
                options = modeDict.pop('options', [])

                for direction in modeDict['direction_options']:
                    for k in data['direction'][direction]:
                        dir_opt = modeDict['direction_options'][direction].copy()
                        dir_opt["key"] = k

                        options.append(dir_opt)

                del modeDict['direction_options']
                modeDict['options'] = options
    
            self.config.extend(Mode(**modeDict).getModeConfig())
            self.append_string_keymap(Mode(**modeDict).getStart().getKeymapDesc())
            self.append_string_same('')

        self.append_string_config(header('bar'))

        bar = data['bar']

        self.append_string_config(Bar(bar['exec'], bar['params']).get())

        config = '\n'.join(self.config)
        keymap = '\n'.join(self.keymap)

        with open(f'{i3_dir}/config', "w") as file:
            file.write(config)
            logging.info(f"Created config {i3_dir}/config")

        with open(i3_keymap, "w") as file:
            file.write(keymap)
            logging.info(f"Created keymap {i3_keymap}")

        # TODO
        # shutil.copytree(f'{config_dir}/display', f'{i3_dir}/display', dirs_exist_ok=True)

    def append_key(self, k):
        for line in k.getKeybinding():
            self.append_string_config(line)
        self.append_string_keymap(k.getKeymapDesc())

    def append_string(self, config='', keymap=''):
        self.append_string_config(config)
        self.append_string_keymap(keymap)

    def append_string_same(self, line=''):
        self.append_string(line, line)

    def append_string_config(self, config=''):
        self.config.append(config)

    def append_string_keymap(self, keymap=''):
        self.keymap.append(keymap)