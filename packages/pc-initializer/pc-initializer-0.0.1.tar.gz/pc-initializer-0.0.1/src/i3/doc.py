from key import Key
from cmd import Cmd
import key
import wsp
import mode

class Table:
    def __init__(self, columns = ['modifier', 'key', 'command', 'description']):
        self.columns = columns
        self.rows = []

    def addKey(self, key):
        row = [
            '+'.join(key.getModifier()),
            key.key,
            key.cmd.getCmd(),
            key.desc
        ]

        self.rows.append(row)



    def getMd(self):
        md = '|'

        line = '|'

        for c in self.columns:
            md += f'{c}|'
            line += '-|'

        md += '\n'
        line += '\n'

        md += line

        for row in self.rows:
            md += '|'
            for c in row:
                md += f'{c}|'
            md += '\n'


        return md

def create_keybindings_md(dir):
    tables = {}

    for section in key.all:
        t = Table()

        for k in key.all[section]:
            t.addKey(k)

        tables[section] = t

    t = Table()
    for workspace in wsp.workspaces:
        t.addKey(workspace.switch)
    for workspace in wsp.workspaces:
        t.addKey(workspace.move)
    for workspace in wsp.workspaces:
        t.addKey(workspace.move_and_switch)

    tables['workspaces'] = t

    for section in media.all:
        t = Table()

        for k in media.all[section]:
            t.addKey(k)

        tables[section] = t

    t = Table()
    for k in border.keys:
        t.addKey(k)
    tables['border'] = t

    modes = {}

    for m in mode.all:
        mode_tables = []
        t = Table()
        t.addKey(m.getStart())

        mode_tables.append(t)

        t = Table()
        for o in m.options:
            t.addKey(o)

        mode_tables.append(t)


        modes[m.name] = mode_tables 


    with open(f'{dir}/i3-keybindings.md', 'w') as md:
        for section in tables:
            md.write(f'# {section}\n') 
            md.write(tables[section].getMd())
            md.write('\n')

        md.write('# Modes\n')
        for name in modes:
            md.write(f'## {name}\n')

            for t in modes[name]:
                md.write(t.getMd())
                md.write('\n')
