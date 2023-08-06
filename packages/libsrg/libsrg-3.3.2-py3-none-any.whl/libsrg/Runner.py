import logging
import subprocess
from pathlib import Path
from typing import List, Optional


class Runner:
    """
    Runner is a utility class to run a command as a subprocess and return results
    * command is passed as a list of program followed by zero or more arguments
      * if provided as a single string, call split to make it a list
    * Runner objects are single use
      * command executed by constructor
      * results returned as fields of object
    * stdout and stderr are captured and returned as lists of utf-8 strings
      * one list element per line
      * end of line chars removed
      * empty list if no output captured
    * return code as integer
    * any exception raised is caught
      * returned in caught field
      * logged as an error
      * optionally rethrown if rethrow is set True
    * success field is true if no exceptions caught and return code is zero
    """

    def __init__(self, cmd: List[str] | str, timeout=None, rethrow=False, verbose=False,
                 cwd: Optional[str | Path] = None,
                 userat: Optional[str] = None):
        """
        Run the given command and return results

        :param cmd: A list of strings, or a single string which Runner will str.split()
        :param timeout: If positive, number of seconds before a timeout exception is raised
        :param rethrow: If true, rethrow any exceptions caught, else success set False
        :param verbose: If true, log the command before execution
        :param cwd: If set, run in this location on local node
        :param userat: Prepend ssh to cammand with this user@remote.node string

        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # _cmd is a list of program name and zero or more arguments
        # split it into a list if provided as a string
        if isinstance(cmd, str):
            self._cmd = cmd.split()
        else:
            self._cmd = cmd
        if userat:
            self._cmd = ["ssh", userat] + self._cmd
        # timeout (if specified) is a timeout to communicate in seconds
        self.userat = userat
        self.success = False
        self.so_bytes: bytearray
        self.se_bytes: bytearray
        self.verbose = verbose
        self.cwd = cwd
        self.ret: int = -1
        self.so_lines: List[str] = []
        self.se_lines: List[str] = []
        self.caught: Optional[Exception] = None
        self.p = None
        self.rethrow = rethrow
        self.timeout = timeout
        self._run_subprocess()
        if verbose:
            self.log()

    def log(self, lgr: logging.Logger = None, throw=False):
        if not lgr:
            lgr = self.logger
        if self.success:
            lgr.info(f'Runner success={self.success} ret={self.ret} _cmd={self._cmd}  so_lines={self.so_lines}')
        else:
            # noinspection PyPep8
            lgr.warning(
                f'Runner success={self.success} ret={self.ret} _cmd={self._cmd}  so_lines={self.so_lines} se_lines={self.se_lines} ')
            if throw:
                raise ChildProcessError(str(self))

    def raise_if_failed(self,lgr: logging.Logger = None,):
        self.log(lgr=lgr,throw=True)

    def _run_subprocess(self):
        if self.verbose:
            self.logger.debug(self._cmd)
        try:
            self.p = subprocess.Popen(self._cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
            (self.so_bytes, self.se_bytes) = self.p.communicate(timeout=self.timeout)
            self.ret = self.p.wait()
            so_str0 = self.so_bytes.decode("utf-8")
            self.so_lines = so_str0.splitlines(keepends=False)
            se_str0 = self.se_bytes.decode("utf-8")
            self.se_lines = se_str0.splitlines(keepends=False)
            self.success = self.ret == 0
        except Exception as ex:
            self.logger.error(ex)
            self.success = False
            self.caught = ex
            if self.rethrow:
                raise ex

    def __str__(self):
        # noinspection PyPep8
        return f'Runner success={self.success} ret={self.ret} _cmd={self._cmd}  so_lines={self.so_lines} se_lines={self.se_lines}'
