from comandor.settings import loadSetting, Setting
from comandor.log import log, FORMAT, DATEFMT
from comandor.models import Action

from tqdm.contrib.logging import logging_redirect_tqdm
from tqdm import tqdm

from typing import Tuple, List

import subprocess as sp
import argparse
import sys


# read args
# return logfile, config, debug settings
def read_args() -> Tuple[str, str, bool]:
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', "--logfile", type=str,
                        default="", help='where save logfile')
    parser.add_argument('-c', "--config", type=str, default=".comandor",
                        help='where you have config file')
    parser.add_argument('-d', "--debug", action='store_true',
                        required=False, help='run debug mod')

    args = parser.parse_args()
    logfile: str = args.logfile
    config: str = args.config
    debug: bool = args.debug
    return (logfile, config, debug)


# setup new config log and load setting form file
def newConfig(logfile: str, config: str, debug: bool) -> Setting:
    setting: Setting = loadSetting(config)
    level: int = log.INFO
    handlers: List = []

    if debug or setting.debug:
        level = log.DEBUG

    if logfile or setting.logfile:
        filename = logfile or str(setting.logfile)
        filemode = "a"
        handlers = [
            log.FileHandler(filename, filemode),
            log.StreamHandler(sys.stdout)
        ]

    log.basicConfig(
        level=level,
        format=FORMAT,
        datefmt=DATEFMT,
        handlers=handlers)

    if debug or setting.debug:
        log.debug("run debug mode!")

    log.debug("logger configure!")
    log.debug("loaded Setting!")
    return setting


# handle 2 type error
# 1- call error system error for your command
# 2- timeout error
def errorHandel(func):
    def wrapper(*a, **kw):
        try:
            log.debug("Run runAction Function")
            return func(*a, **kw)

        except sp.CalledProcessError as err:
            log.error(
                f"Status : FAIL Code: {err.returncode}\n"
                f"OutPut:\n {err.output.decode()}")
            raise

        except sp.TimeoutExpired:
            log.error("Timeout Error!")
            raise

    return wrapper


@errorHandel
def runActions(actions: List[Action]):
    log.debug("Run action from actions list")

    for action in tqdm(actions):
        log.info(f"---- Processing {action.action_name} ----")

        command = f"cd {action.path} && " + " && ".join(action.commands)

        log.info(f"run this command: {command}")
        log.info(f"run with timeout: {action.timeout}")

        log.debug("run command")
        outProcess = sp.check_output(command, shell=True, stderr=sp.STDOUT,
                                     timeout=action.timeout)

        log.debug("print result from Process")
        log.info(outProcess.decode())
        log.info(f"---- Done Process {action.action_name} ----\n")

    log.info("---- Done All Task! ----")


def main():
    setting: Setting = newConfig(*read_args())

    log.info(f"start commander -> {setting.name}")
    with logging_redirect_tqdm():
        runActions(setting.actions)


if __name__ == "__main__":
    main()
