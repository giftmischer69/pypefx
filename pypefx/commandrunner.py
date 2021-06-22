import logging
import os
import subprocess


class CommandRunner:
    debug = False

    @classmethod
    def run_checked(cls, command):
        logging.debug(f"CWD: {os.getcwd()}")
        logging.debug(f"running command: {command}")
        if cls.debug:
            stdout = subprocess.STDOUT
        else:
            stdout = subprocess.DEVNULL

        proc = subprocess.run(command, stdout=stdout, stderr=subprocess.DEVNULL)
        return_code = proc.returncode
        logging.debug(f"return_code: {return_code}")
        if return_code != 0:
            logging.error(str(proc.__dict__))
            raise Exception(proc.stdout)
