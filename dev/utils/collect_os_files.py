import logging
import os

import parts
import multiprocessing
import subprocess
from subprocess import PIPE
import time

from collections import defaultdict
from src.shell.bashlex.main import *
from src.containerfile.tpdockerfile.main import *
from dev.utils.data_utils import *


def log_header(s: str) -> str:
    return f"{s.upper()}:"


def flag_print(*args, **kwargs):
    if "echo" in kwargs and kwargs["echo"]:
        del kwargs["echo"]
        print(*args, **kwargs)


def os_specific_containerfiles(os_names: List[str], directory: str) -> Dict[str, List[str]]:
    shell_parser = BashlexShellParser()
    df_parser = TPDockerfileParser(shell_parser=shell_parser)
    res = defaultdict(list)
    paths = filepaths_from_dir(directory)

    for path in tqdm(paths, desc="Collecting filenames", smoothing=1.0):
        try:
            with open(path.strip(), "r") as df:
                source = "".join(df.readlines())

            content = df_parser.from_str(source)
            from_directive = next(x for x in content.directives if isinstance(x, FromDirective))

            for os_name in os_names:
                if from_directive.values[0].startswith(os_name):
                    res[os_name].append(path)
        except Exception as exc:
            globalLog.info(type(exc), exc)

    return res


def filter_containerfiles_worker(args: Tuple[List[str], int, bool, str]) -> List[str]:
    paths, idx, echo, log_dir = args
    res = []

    with tqdm(total=len(paths), position=idx, desc=f"Loop {idx}") as pbar:
        for path in paths:
            name = path[path.rfind("/") + 1:]
            name = name[:name.find(".")]
            image_name = f"filter-{name}"
            build_comm = f"docker build -t {image_name} --file={path} ."
            rm_comm = f"docker image rm {image_name}"

            try:
                flag_print(build_comm, echo=echo)
                build_res = subprocess.run(["/bin/bash", "-c", build_comm],
                                           stdout=PIPE, stderr=PIPE, text=True, timeout=240)

                success = True if build_res.returncode == 0 else False
                build_stdout, build_stderr = build_res.stdout, build_res.stderr
            except subprocess.TimeoutExpired:
                success = False
                build_stdout, build_stderr = "", "Time limit exceeded"
            if success:
                res.append(path)

            flag_print(rm_comm, echo=echo)
            rm_res = subprocess.run(["/bin/bash", "-c", rm_comm], stdout=PIPE, stderr=PIPE, text=True)

            log_path = os.path.join(log_dir, image_name)
            with open(log_path, "w") as outF:
                outF.writelines([
                    log_header("IMAGE NAME") + f"{image_name}\n\n",
                    log_header("CONTAINERFILE PATH") + f"{path}\n\n",
                    log_header("BUILD COMMAND") + f"{build_comm}\n\n",
                    log_header("BUILD SUCCESS") + f"{success}\n\n",
                    log_header("BUILD STDOUT") + f"{build_stdout.strip()}\n\n",
                    log_header("BUILD STDERR") + f"{build_stderr.strip()}\n\n",
                    log_header("RM COMMAND") + f"{rm_comm}\n\n",
                    log_header("RM STDOUT") + f"{rm_res.stdout}\n\n",
                    log_header("RM STDERR") + f"{rm_res.stderr}\n\n"
                ])
            pbar.update(1)

    return res


def filter_containerfiles(paths: List[str], n_proc: int, log_dir: str) -> List[str]:
    echo = False
    with multiprocessing.Pool(processes=n_proc) as pool:
        spans = parts.parts(paths, n_proc)
        per_proc = pool.map(filter_containerfiles_worker,
                            [(list(span), idx, echo, log_dir) for span, idx in zip(spans, range(n_proc))])
        res = [good_run for p in per_proc for good_run in p]
    return res


def collect_containerfiles():
    os_directories = {
        "ubuntu": UBUNTU_FILES_DIR
    }

    os_filepaths = os_specific_containerfiles(list(os_directories.keys()), directory=ALL_FILES_DIR)

    for os_name, os_dir in os_directories.items():
        paths = os_filepaths[os_name]
        setup_dir(os_dir)
        copy_files(paths, os_dir)


def pulpify_containerfiles(names: List[str], in_dir: str, out_dir: str):
    for name in tqdm(names):
        with open(os.path.join(in_dir, name), "r") as in_f:
            lines = []
            flag = True
            for line in in_f:
                if line.startswith("FROM"):
                    lines.append("FROM ubuntu-pulp\n")
                elif line.startswith("COPY"):
                    flag = False
                    break
                else:
                    lines.append(line)

        if flag:
            with open(os.path.join(out_dir, name), "w") as out_f:
                out_f.writelines(lines)


def filter_and_copy_containerfiles(in_dir: str, out_dir: str, log_dir: str, n_proc: int):
    filepaths = filepaths_from_dir(in_dir)
    setup_dir(log_dir)
    filtered_paths = filter_containerfiles(filepaths, n_proc=n_proc, log_dir=log_dir)
    copy_files(filtered_paths, out_dir)


def main():
    # collect_containerfiles()

    pulped_dir = os.path.join(UBUNTU_DATA_DIR, "pulped")
    setup_dir(pulped_dir)

    in_dir = pulped_dir
    # in_dir = UBUNTU_FILES_DIR
    out_dir = UBUNTU_FILTERED_FILES_DIR
    log_dir = UBUNTU_FILTERED_FILES_LOG_DIR
    n_proc = 4

    # pulpify_containerfiles(filenames_from_dir(UBUNTU_FILES_DIR), UBUNTU_FILES_DIR, pulped_dir)
    filter_and_copy_containerfiles(in_dir=in_dir, out_dir=out_dir, log_dir=log_dir, n_proc=n_proc)


if __name__ == "__main__":
    globalLog.setLevel(logging.ERROR)
    main()
