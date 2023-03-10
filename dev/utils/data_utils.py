import logging
import os.path
import os
import shutil
from tqdm import tqdm
from typing import List, Iterable

from src.shell.main import ShellCommandObject, ShellScript
from src.shell.bashlex.main import BashlexShellParser
from src.containerfile.main import RunDirective, DockerfileContent
from src.containerfile.tpdockerfile.main import TPDockerfileParser
from src.log import globalLog


DEV_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(DEV_DIR, 'data')
LOG_DIR = os.path.join(DATA_DIR, 'log')
SANDBOX_DIR = os.path.join(DEV_DIR, 'sandbox')
CONTAINERFILES_ARCHIVE = os.path.join(DATA_DIR, 'files.tar.xz')
CONTAINERFILES_DIR = os.path.join(DATA_DIR, 'files')
UBUNTU_CONTAINERFILES_DIR = os.path.join(DATA_DIR, 'ubuntu_files')
DEBIAN_CONTAINERFILES_DIR = os.path.join(DATA_DIR, 'debian_files')
MINED_SHELL_COMMANDS_FILE = os.path.join(DATA_DIR, 'mined_commands')
MINED_UBUNTU_SHELL_COMMANDS_FILE = os.path.join(DATA_DIR, 'mined_ubuntu_commands')
MINED_DEBIAN_SHELL_COMMANDS_FILE = os.path.join(DATA_DIR, 'mined_debian_commands')
COLLECTED_MATCHER_TESTS_FILE = os.path.join(DATA_DIR, "collected_matcher_tests")
FILTERED_MATCHER_TESTS_FILE = os.path.join(DATA_DIR, "filtered_matcher_tests_0")


def filenames_from_dir(directory: str) -> List[str]:
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def filepaths_from_dir(directory: str) -> List[str]:
    return [os.path.join(directory, f) for f in filenames_from_dir(directory)]


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def mine_shell_commands(files_dir: str, output_file: str) -> None:
    sh_parser = BashlexShellParser()
    cf_parser = TPDockerfileParser(shell_parser=sh_parser)

    commands = []
    filenames = filenames_from_dir(files_dir)
    for name in tqdm(filenames, desc="Mining shell"):
        path = os.path.join(files_dir, name)
        try:
            with open(path.strip(), "r") as cf:
                source = "".join(cf.readlines())
                source.replace("\t", " ")

            content = cf_parser.from_str(source)
            for run_dir in content.directives:
                if isinstance(run_dir, RunDirective):
                    line = run_dir.line
                    line.replace("\n", " ")

                    for comm in run_dir.script.parts:
                        if isinstance(comm, ShellCommandObject):
                            line = comm.line
                            line.replace("\t", " ")
                            commands.append(line + "\n")
        except Exception:
            pass

    with open(output_file, "w") as outF:
        outF.writelines(commands)


def copy_files(paths: List[str], directory: str) -> None:
    for path in tqdm(paths, desc="Copying files", smoothing=1.0):
        shutil.copy2(path, directory)


if __name__ == "__main__":
    globalLog.setLevel(logging.ERROR)
