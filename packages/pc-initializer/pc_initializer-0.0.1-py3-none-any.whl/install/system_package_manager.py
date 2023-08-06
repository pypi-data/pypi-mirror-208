import logging

from install.apt import Apt
from install.dnf import Dnf
from install.pacman import Pacman
from install.winget import WinGet

from util.os import OS, OSDetector

switcher = {
    OS.FEDORA: Dnf,
    OS.MANJARO: Pacman,
    OS.UBUNTU: Apt,
    OS.WINDOWS: WinGet
}

class SystemPackageManager:
    def __init__(self):
        self.os = OSDetector.getOs()
        self.package_manager = switcher.get(self.os, lambda args: print(f"Package manager for '{os}' not implemented"))()
        self.name = type(self.package_manager).__name__.lower()

    def install(self, packages, dry_run = True):
        # packages = data[self.name]
        self.package_manager.install(packages, dry_run)
