import os.path
import os
import zipfile
from tqdm import tqdm
from typing import List

from src.shell.main import ShellCommandObject, ShellScript
from src.shell.bashlex.main import BashlexShellParser
from src.containerfile.main import RunDirective, DockerfileContent
from src.containerfile.tpdockerfile.main import TPDockerfileParser


DEV_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(os.path.dirname(DEV_DIR), 'data')
SANDBOX_DIR = os.path.join(DEV_DIR, 'sandbox')
CONTAINERFILES_ARCHIVE = os.path.join(DATA_DIR, 'files.zip')
CONTAINERFILES_DIR = os.path.join(DATA_DIR, 'files')
MINED_SHELL_COMMANDS_FILE = os.path.join(DATA_DIR, 'mined_commands')


def filenames_from_dir(directory: str) -> List[str]:
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def filepaths_from_dir(directory: str) -> List[str]:
    return [os.path.join(directory, f) for f in filenames_from_dir(directory)]


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def extract_containerfiles() -> None:
    with zipfile.ZipFile(CONTAINERFILES_ARCHIVE, 'r') as zipF:
        for member in tqdm(zipF.infolist(), desc="Extracting"):
            try:
                zipF.extract(member, DATA_DIR)
            except zipfile.error as e:
                pass


def mine_shell_commands() -> None:
    sh_parser = BashlexShellParser()
    cf_parser = TPDockerfileParser(shell_parser=sh_parser)

    commands = []
    filenames = filenames_from_dir(CONTAINERFILES_DIR)
    for i, name in tqdm(enumerate(filenames), desc="Mining shell"):
        path = os.path.join(CONTAINERFILES_DIR, name)
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

    with open(MINED_SHELL_COMMANDS_FILE, "w") as outF:
        outF.writelines(commands)


if __name__ == "__main__":
    extract_containerfiles()
