from enum import Enum
from jproperties import Properties

import sys

class OS(Enum):
    FEDORA = 1
    MANJARO = 2
    UBUNTU = 3
    WINDOWS = 4

class OSDetector:
    @staticmethod
    def getOs():
        if sys.platform == 'win32':
            return OS.WINDOWS
        else:
            p = Properties()
            with open("/etc/os-release", "rb") as f:
                p.load(f, "utf-8")

            id = p.get('ID').data.lower()

            match id:
                case 'fedora':
                    return OS.FEDORA
                case 'manjaro':
                    return OS.MANJARO
                case 'ubuntu':
                    return OS.UBUNTU

            raise Exception(f'OS "{id}" not supported')
