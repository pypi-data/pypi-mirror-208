import configparser
import os
import platform
from importlib.metadata import version

from libsrg.Runner import Runner

class Info:
    def __init__(self, hostname: str = None):
        self.ver = version('libsrg')
        self.node = platform.node()
        self.node0 = self.node.split('.')[0]
        self.config = configparser.ConfigParser()
        self.uname = os.uname()

        if hostname:
            userat = f"root@{hostname}"
            self.hostname = hostname
        else:
            userat = None
            self.hostname = self.node0

        r = Runner("cat /etc/os-release", userat=userat)
        if not r.success:
            raise Exception(f"os-release failed for {userat}")
        data = r.so_lines
        # add a section header
        data.insert(0, "[osrelease]")
        self.config.read_string("\n".join(data))
        # for key in self.config:
        #     self.logger.info(key)
        osrelease = self.config['osrelease']
        self.osrelease = osrelease
        # for key, val in osrelease.items():
        #     self.logger.info(f"{key} = {val}")

        # fedora has 'id' lower case, raspian upper
        # configparser says keys are case insensitive
        self.id = osrelease['ID']
        if 'id' in osrelease:
            self.id = osrelease['id']
        else:
            self.id = 'unknown'
            self.logger.error(f"'id' not found in {osrelease}")

        # raspian 'ID_LIKE' says, "But you can call me Debian"
        if 'ID_LIKE' in osrelease:
            self.id_like = osrelease['ID_LIKE']
        else:
            self.id_like = self.id
        # self.logger.info(f"id={self.id}, id_like={self.id_like} ")

        if 'PRETTY_NAME' in osrelease:
            self.pretty_name = osrelease['PRETTY_NAME'].replace('"', '')
        else:
            self.pretty_name = self.id + " " + osrelease['VERSION_ID']


if __name__ == '__main__':
    #info = Info("nas0")
    info = Info()
    print(f"In version {info.ver} {__file__} on {info.node}")
    print(f"{info.hostname} {info.id} {info.id_like} {info.pretty_name}")
    print(info.uname)
