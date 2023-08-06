#! /usr/bin/env python3

# cd /GNAS/PROJ/PycharmProjects/libsrg
# venvF/bin/python -m libsrg.ReZFS --source

# noinspection PyPep8
"""
Manual procedure to install from source:

dnf install --skip-broken epel-release gcc make autoconf automake libtool rpm-build kernel-rpm-macros libtirpc-devel
  libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel
  kernel-devel-$(uname -r) python3 python3-devel python3-setuptools python3-cffi libffi-devel ncompress

dnf install --skip-broken --enablerepo=epel --enablerepo=powertools python3-packaging dkms
dnf remove zfs-fuse
cd /etc/yum.repos.d/
ls
mv zfs.repo zfs.repo.patched
cd  # ~root
git clone https://github.com/zfsonlinux/zfs.git
cd zfs
./autogen.sh
./configure
make -j1 rpm-utils rpm-dkms
yum localinstall *.$(uname -p).rpm *.noarch.rpm
zpool list
zpool import -a
zpool list

"""

import configparser
import logging
import os
from enum import Enum
from importlib.metadata import version
from pathlib import Path

from libsrg.LoggingAppBase import LoggingAppBase
from libsrg.Runner import Runner


# rpm --force -U --reinstall https://zfsonlinux.org/fedora/zfs-release$(rpm -E %dist).noarch.rpm  --verbose
# rpm --badreloc --force -U --reinstall https://zfsonlinux.org/fedora/zfs-release$(rpm -E %dist).noarch.rpm
#      --verbose --root=/tmp/Z --nodeps --noscripts
class Mode(Enum):
    NOMODE = -1
    REPAIR = 0
    INSTALL = 1
    PATCH = 2
    UNPATCH = 3
    SOURCE = 4


class ReZFS(LoggingAppBase):
    supported_os = ["fedora"]

    # noinspection PyPep8
    def __init__(self):
        super().__init__()
        self.pretty_name = None
        self.id_like = None
        self.id = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parser.set_defaults(mode=Mode.REPAIR)
        self.parser.add_argument('--version', action='version', version=f"libsrg {version('libsrg')}")
        # noinspection PyPep8
        self.parser.add_argument('--repair',
                                 help="kill old dkms and rebuild (will not install if zfs repo file missing)" +
                                      " (default mode)", dest='mode', action='store_const', const=Mode.REPAIR)
        self.parser.add_argument('--source',
                                 help="install from source, remove repo file if found",
                                 dest='mode', action='store_const', const=Mode.SOURCE)
        self.parser.add_argument('--install',
                                 help="install from repo on new or existing zfs node, patch if current repo not found",
                                 dest='mode', action='store_const', const=Mode.INSTALL)
        self.parser.add_argument('--patch', help="patch repo file for N-1, then install (even if current repo exists)",
                                 dest='mode', action='store_const', const=Mode.PATCH)
        self.parser.add_argument('--unpatch', help="revert to unpatched repo file, then install", dest='mode',
                                 action='store_const', const=Mode.UNPATCH)
        self.parser.add_argument('--osrelease', help='OS Release file (/etc/os-release)', dest='osrelease',
                                 type=str, default="/etc/os-release")
        self.parser.add_argument('--zfsrel', help='ZFS release url prefix', dest='zfsrel',
                                 type=str, default="https://zfsonlinux.org/fedora/zfs-release-2-3")
        self.parser.add_argument('--zfsrel2', help='ZFS release url suffix', dest='zfsrel2',
                                 type=str, default=".noarch.rpm")
        self.parser.add_argument('--remove', help='removed prior install', dest='remove',
                                 action='store_true', default=False)

        self.parser.description = "rezfs.py is a tool to update zfs installation across updates of Fedora"
        self.parser.prog = "rezfs.py"
        self.parser.allow_abbrev = True
        self.parser.epilog = "--repair is assumed if no other mode options are selected"
        self.perform_parse()
        self.config = configparser.ConfigParser()
        self.read_release_id()
        self.osrelease = self.config['osrelease']
        id_ = self.osrelease["id"]
        if id_ not in self.supported_os:
            self.logger.critical(f"OS not supported: {id_} not in {self.supported_os}")
            exit(-1)

        # current is version N of running os
        # previous is N-1
        self.current_version_number = int(self.osrelease["version_id"])
        self.current_dist = f".fc{self.current_version_number}"
        self.previous_version_number = self.current_version_number - 1
        self.previous_dist = f".fc{self.previous_version_number}"

        self.repo_path = Path("/etc/yum.repos.d/zfs.repo")
        self.repo_path_old = Path("/etc/yum.repos.d/zfs.repo.old")
        self.uname = os.uname()
        self.release = self.uname.release  # uname -r

        uid = os.getuid()

        if uid != 0:
            self.logger.critical(f"This program must be run as root(0), {uid=}")
            exit(-1)

        if self.args.mode == Mode.SOURCE:
            self.install_from_source()
        else:
            self.install_from_repo()

    def install_requirements(self):

        # noinspection PyPep8
        cmd_str = "/usr/bin/dnf install -y --skip-broken epel-release gcc make autoconf automake " + \
                  "libtool rpm-build kernel-rpm-macros libtirpc-devel libblkid-devel libuuid-devel" + \
                  " libudev-devel openssl-devel"
        # noinspection PyPep8
        cmd_str += " zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-devel-" + self.release + \
                   " python3 python3-devel python3-setuptools python3-cffi libffi-devel ncompress"
        cmd = cmd_str.split()
        self.logger.info(cmd)
        r = Runner(cmd, verbose=True, timeout=120)

        # noinspection PyPep8
        cmd_str = "/usr/bin/dnf install -y --skip-broken --enablerepo=epel --enablerepo=powertools " + \
                  "python3-packaging dkms"
        cmd = cmd_str.split()
        r = Runner(cmd, verbose=True, timeout=120)

        cmd = "dnf remove zfs zfs-dkms zfs-fuse --noautoremove -y".split()
        r = Runner(cmd, verbose=True, timeout=10)

    def install_from_source(self):
        # https://github.com/openzfs/zfs
        # https://openzfs.github.io/openzfs-docs/Developer%20Resources/Building%20ZFS.html?highlight=source
        self.logger.info(f"Begin install from source {self.args.mode}")
        self.repo_path.unlink(missing_ok=True)
        self.install_requirements()

        # prepare directory for build
        tgt1 = Path("/tmp/ZFS_SRC")
        tgt2 = tgt1 / "zfs"
        r = Runner(["rm", "-rf", str(tgt1)], timeout=60)
        tgt1.mkdir()

        r = Runner(["git", "clone", "https://github.com/zfsonlinux/zfs.git"], cwd=tgt1, verbose=True)

        r = Runner(["./autogen.sh"], cwd=tgt2, verbose=True, timeout=300)
        r = Runner(["./configure"], cwd=tgt2, verbose=True, timeout=300)

        r = Runner("make -j1 rpm-utils rpm-dkms".split(), cwd=tgt2, verbose=True, timeout=600)

        rpm1 = tgt2.glob("*.x86_64.rpm")
        rpm2 = tgt2.glob("*.noarch.rpm")
        cmd = "yum localinstall -y".split()
        cmd.extend([str(x) for x in rpm1])
        cmd.extend([str(x) for x in rpm2])
        self.logger.info(cmd)
        r = Runner(cmd, cwd=tgt2, verbose=True, timeout=300)

        if not self.modprobe_zfs():
            self.logger.critical("driver failed to load")
            exit(-1)
        self.mount()

    def install_from_repo(self):
        self.logger.info(f"Begin install from repo {self.args.mode}")
        if not self.repo_path.exists():
            if self.args.mode == Mode.REPAIR:
                self.logger.info(f"{self.repo_path} not found -- {self.args.mode} will terminate")
                exit(-1)
        self.repo_install()
        if self.args.mode == Mode.PATCH:
            self.patch_repo_file()
        self.install()
        self.mount()

    def patch_repo_file(self):
        # note that each line includes a terminating newline character
        with open(self.repo_path, 'r') as fp:
            lines = fp.readlines()
        plines = [line.replace("$releasever", str(self.previous_version_number)).replace("ZFS on Linux for",
                                                                                         "ZFS on Linux Patched for") for
                  line in lines]
        plines.insert(0, f"#Patched {self.previous_dist} repo file for temporary use on {self.current_dist}" + "\n")
        with open(self.repo_path_old, 'w') as fp:
            fp.writelines(lines)
        with open(self.repo_path, 'w') as fp:
            fp.writelines(plines)
        self.logger.info(f"new= {self.repo_path} old= {self.repo_path_old}")
        # for pline in plines:
        #     self.logger.info(pline)

    def repo_install(self):
        self.repo_path.unlink(missing_ok=True)
        if not self.repo_tryinstall(self.current_dist):
            if not self.repo_tryinstall(self.previous_dist):
                self.logger.critical("Could not load repo file")
                exit(-1)
            self.args.mode = Mode.PATCH
            self.logger.warning(f"Changing mode to {self.args.mode} to try installing " +
                                f"on {self.current_version_number} with {self.previous_version_number} repo")

    def repo_tryinstall(self, distro: str) -> bool:
        rpm = self.args.zfsrel + distro + self.args.zfsrel2
        cmd = ["rpm", "--force", "-U", "--reinstall", rpm]
        r = Runner(cmd)
        if r.success:
            self.logger.info(f"Successfully loaded {rpm} {cmd}")
        else:
            self.logger.warning(f"Failed to load {rpm} {cmd}")
        return r.success

    def modprobe_zfs(self) -> bool:
        cmd = ["modprobe", "zfs"]
        r = Runner(cmd)
        self.logger.info(f"{r.success=}")
        return r.success

    def read_release_id(self):
        with open(self.args.osrelease, 'r') as fp:
            data = fp.readlines()
        # add a section header
        data.insert(0, "[osrelease]")
        self.config.read_string("\n".join(data))
        # for key in self.config:
        #     self.logger.info(key)
        osrelease = self.config['osrelease']
        # for key,val in osrelease.items():
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
            self.pretty_name = osrelease['PRETTY_NAME']
        else:
            self.pretty_name = self.id

        self.logger.info(f"id={self.id}, id_like={self.id_like} pretty_name={self.pretty_name}")

    def install(self):
        if not self.modprobe_zfs() or self.args.remove:
            cmd = "dnf remove zfs zfs-dkms zfs-fuse --noautoremove -y".split()
            r = Runner(cmd)
            self.logger.info(f"{r.success=} {cmd}")
            #
            cmd = "rm -rf /var/lib/dkms/zfs".split()
            r = Runner(cmd)
            self.logger.info(f"{r.success=} {cmd}")
            #
            self.logger.info("Installing...  (takes about two minutes)")
            cmd = "dnf install zfs -y".split()
            r = Runner(cmd, timeout=240)
            self.logger.info(f"{r.success=} {cmd}")
            if not r.success:
                self.logger.error(r.so_lines)
                self.logger.error(r.se_lines)
                exit(-1)
        if not self.modprobe_zfs():
            self.logger.critical("driver failed to load")
            exit(-1)

    def mount(self):
        cmd = "zpool status ZRaid".split()
        r = Runner(cmd)
        self.logger.info(f"{r.success=} {cmd}")
        if not r.success:
            cmd = "zpool import -a -d /dev/disk/by-id".split()
            r = Runner(cmd)
            self.logger.info(f"{r.success=} {cmd}")
        cmd = "zpool status".split()
        r = Runner(cmd)
        self.logger.info(f"{r.success=} {cmd}" + "\n" + "\n".join(r.so_lines))
        if not r.success:
            self.logger.critical("Could not mount pools")
            exit(-1)
        cmd = "zfs list".split()
        r = Runner(cmd)
        self.logger.info(f"{r.success=} {cmd}" + "\n" + "\n".join(r.so_lines))
        #
        cmd = "zfs --version".split()
        r = Runner(cmd)
        self.logger.info(f"{r.success=} {cmd}" + "\n" + "\n".join(r.so_lines))


#
# uname -a
# dstring="$(rpm -E %dist)"    # .fc##
# dnum="${dstring:3}"
# pdnum=$((dnum-1))
# pdstring=".fc${pdnum}"
# echo $dstring $dnum
# echo $pdstring $pdnum

# function check {
# if modprobe zfs
# then
#   echo zfs module is loaded
#   if zpool status ZRaid
#   then
#     echo pool found
#   else
#     echo import pool
#     zpool import ZRaid
#     zpool import -a -d /dev/disk/by-id
#     zpool status
#   fi
#   echo "----------------"
#   zpool list
#   echo "----------------"
#   zfs list
#   echo "----------------"
#   zfs --version
#   exit
# else
#   echo zfs module not found - continue reinstall
# fi
# }
#
# check
# echo attempt dnf update
# dnf update zfs -y
# check
# echo ===============================================================================================================
# echo Begin reinstall of zfs
# echo
# dnf remove zfs zfs-dkms zfs-fuse --noautoremove -y
# rm -rf /var/lib/dkms/zfs
# dnf install zfs -y
#
# check


if __name__ == '__main__':
    app = ReZFS()
