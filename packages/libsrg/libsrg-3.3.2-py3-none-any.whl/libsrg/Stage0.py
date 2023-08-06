#!/usr/bin/env  python3

import configparser
import platform
from importlib.metadata import version
from pathlib import Path

from libsrg.LoggingAppBase import LoggingAppBase

from libsrg.Runner import Runner

"""
This module performs stage-0 setup of a new intranet node.

Stage-0
* Install nfs client drivers if needed
* Mount the ansible project code in a temporary directory
* create a python virtual environment
* install ansible in the venv
* display the next commands to be cut/pasted by root

Stage-1 
* invoke ansible in local mode (setup_sshd_as_local.yml)
* install and enable ssh
* install user keys for ansible to push updates from server node

Stage-2
* invoke master.yml from server node to complete setup

"""


class Stage0(LoggingAppBase):

    def __init__(self):
        super().__init__()
        self.pretty_name = None
        self.id_like = None
        self.id = None
        self.uname = platform.uname()
        self.hostnameparts = self.uname.node.split('.')

        self.logger.info("before adding args")
        # setup any program specific command line arguments
        self.parser.add_argument('--version', action='version', version=f"libsrg {version('libsrg')}")
        self.parser.add_argument('--osrelease', help='OS Release file (/etc/os-release)', dest='osrelease',
                                 type=str, default="/etc/os-release")
        self.parser.add_argument('--subdir', help='subdirectory below mount point, no leading or trailing slahshes',
                                 dest='subdir',
                                 type=str, default="PycharmProjects/ANS_PROJECT")
        self.parser.add_argument('--local', help='hard mount point if disk is local', dest='local',
                                 type=str, default="/GNAS/PROJ")
        self.parser.add_argument('--softmount', help='soft mount point if disk is remote', dest='softmount',
                                 type=str, default="/tmp/XPROJX")
        self.parser.add_argument('--remote', help='nfs node/directory to mount', dest='remote',
                                 type=str, default="10.0.4.10:/GNAS/PROJ")
        self.parser.add_argument('--nolocal', help='ignore local mount point if present', dest='nolocal',
                                 action='store_true', default=False)
        self.parser.add_argument('--short', help='short name for node (not FQDN)', dest='short',
                                 type=str, default=self.hostnameparts[0])
        self.parser.add_argument('--domain', help='domain part of FQDN', dest='domain',
                                 type=str, default="home.goncalo.name")

        # /GNAS/GPUB/ansible_gpub
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")
        self.config = configparser.ConfigParser()

        self.local_path = Path(self.args.local)
        self.local_subdir_path = self.local_path / self.args.subdir
        self.softmount_path = Path(self.args.softmount)
        self.softmount_subdir_path = self.softmount_path / self.args.subdir
        self.go_ans_path = self.softmount_subdir_path / "source_ans_env"
        self.grind()
        suggest = "\n".join(["", "", f"For stage 1 setup, execute the following commands:", "",
                             f"source {self.go_ans_path}", f"local_setup", ""])
        self.logger.info(suggest)
        print(suggest)

    def grind(self):
        self.release_id()
        self.fix_hostname()
        self.connect_paths()

    def fix_hostname(self):
        fqdn = f"{self.args.short}.{self.args.domain}"
        if fqdn == self.uname.node:
            self.logger.info(f"FQDN already set to {fqdn}")
        else:
            r = Runner(f"hostnamectl set-hostname --static {fqdn}", verbose=True)
            self.logger.info(f"Node name changed from {self.uname.node} to {fqdn}")

    def connect_paths(self):
        if not self.args.nolocal and self.local_subdir_path.is_dir():
            self.logger.info(f"{self.local_subdir_path} exists, linking")
            self.softmount_path.unlink(missing_ok=True)
            self.softmount_path.symlink_to(self.local_path)
            self.logger.info(f"softlink {self.softmount_path} -> {self.local_path}")
        else:
            self.mount_paths()

    def mount_paths(self):
        self.install_nfs()
        rfm = Runner(["findmnt", str(self.softmount_path)])
        if rfm.success:
            self.logger.info(f"already mounted {rfm}")
        else:
            self.softmount_path.mkdir(parents=True, exist_ok=True)
            rmt = Runner(["mount", "-t", "nfs4", str(self.args.remote), str(self.softmount_path)])
            if not rmt.success:
                self.logger.critical(f"mount failed {rmt}")
                exit(-1)
            self.logger.info(f"mounted {rmt}")

    def release_id(self):
        with open(self.args.osrelease, 'r') as fp:
            data = fp.readlines()
        # add a section header
        data.insert(0, "[osrelease]")
        self.config.read_string("\n".join(data))
        for key in self.config:
            self.logger.info(key)
        osrelease = self.config['osrelease']
        for key, val in osrelease.items():
            self.logger.info(f"{key} = {val}")

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
        self.logger.info(f"id={self.id}, id_like={self.id_like} ")

        if 'PRETTY_NAME' in osrelease:
            self.pretty_name = osrelease['PRETTY_NAME']
        else:
            self.pretty_name = self.id

        self.logger.info(f"id={self.id}, id_like={self.id_like} pretty_name={self.pretty_name}")

    def install_nfs(self):
        r = Runner(["which", "mount.nfs4"])
        if r.success and r.so_lines:
            self.logger.info(f"found {r.so_lines[0]}")
        else:
            cmd = []
            if self.id_like in ["fedora"]:
                cmd = ["dnf", "install", "-y", "nfs-utils"]
            elif self.id_like in ["debian", "ubuntu", "raspian"]:
                cmd = ["apt", "install", "-y", "nfs-common"]
            else:
                self.logger.fatal(f"mount.nfs4 not found, do not know how to install on {self.id_like}")
                exit(-1)
            r2 = Runner(cmd)
            if not r2.success:
                self.logger.fatal(f"failed to install mount.nfs4 {r2}")
                exit(-1)

    @classmethod
    def demo(cls):
        app = Stage0()


if __name__ == '__main__':
    Stage0.demo()
