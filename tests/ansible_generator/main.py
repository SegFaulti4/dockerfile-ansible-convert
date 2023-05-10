import logging
import os
import time
import parts
import multiprocessing
import subprocess
from subprocess import PIPE
from tqdm import tqdm
from typing import List, Tuple, Optional

import cli.main
from tests.utils.data_utils import *

from src.log import globalLog

BASE_IMAGE = "ubuntu-test-stand"
DOCKER_NET_NAME = "test-net"
TIMEOUT = 300


def log_header(s: str) -> str:
    return f"{s.upper()}:"


def flag_print(*args, **kwargs):
    if "echo" in kwargs and kwargs["echo"]:
        del kwargs["echo"]
        print(*args, **kwargs)


def prepare_containerfile_image(file_name: str, idx: int, echo: bool) -> Optional[str]:
    path = os.path.join(GENERATOR_TESTS_DIR, file_name)
    file_basename = file_name[:file_name.find('.')]
    cf_path = os.path.join(TMP_DIR, file_name)
    copy_file(path, cf_path)

    image_name = f"docker-test-{file_basename}"
    build_comm = f"docker build --no-cache --progress=plain -t {image_name} --file={cf_path} ."

    try:
        flag_print(build_comm, echo=echo)
        build_res = subprocess.run(["/bin/bash", "-c", build_comm],
                                   stdout=PIPE, stderr=PIPE, text=True, timeout=TIMEOUT)

        success = True if build_res.returncode == 0 else False
        build_stdout, build_stderr = build_res.stdout, build_res.stderr
    except subprocess.TimeoutExpired:
        success = False
        build_stdout, build_stderr = "", "Time limit exceeded"
    except UnicodeDecodeError:
        success = False
        build_stdout, build_stderr = "", "Unicode shenanigans"

    log_path = os.path.join(LOG_DIR, image_name)
    with open(log_path, "w") as outF:
        outF.writelines([
            log_header("IMAGE NAME") + f"{image_name}\n\n",
            log_header("CONTAINERFILE PATH") + f"{cf_path}\n\n",
            log_header("BUILD COMMAND") + f"{build_comm}\n\n",
            log_header("BUILD SUCCESS") + f"{success}\n\n",
            log_header("BUILD STDOUT") + f"{build_stdout.strip()}\n\n",
            log_header("BUILD STDERR") + f"{build_stderr.strip()}\n\n"
        ])

    if success:
        return image_name
    else:
        return None


def prepare_ansible_image(file_name: str, idx: int, echo: bool) -> Optional[str]:
    path = os.path.join(GENERATOR_TESTS_DIR, file_name)
    file_basename = file_name[:file_name.find('.')]
    pb_path = os.path.join(TMP_DIR, file_basename + ".yml")

    try:
        with open(pb_path, "w") as outF:
            cli.main.generate(containerfile_path=path, output=outF)
    except Exception:
        print(f"Failed to generate playbook from dockerfile - {path}")
        return None

    ip_addr = f"172.18.0.{idx + 2}"
    image_name = f"ansible-test-{file_basename}"
    container_name = f"{image_name}-container"

    run_comm = f"docker run -d --net {DOCKER_NET_NAME} --ip {ip_addr} -p {8000 + idx}:22 " \
               f"--name={container_name} {BASE_IMAGE}"
    ansible_comm = f'/usr/bin/ansible-playbook -vv {pb_path} --ssh-common-args="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --user=root --inventory="{ip_addr},"'
    commit_comm = f"docker commit {container_name} {image_name}"
    stop_rm_comm = f"docker stop {container_name} && docker rm {container_name}"

    def shell_try(comm):
        try:
            flag_print(comm, echo=echo)
            res = subprocess.run(["/bin/bash", "-c", comm], stdout=PIPE, stderr=PIPE, text=True,
                                 timeout=TIMEOUT)
            time.sleep(0.5)
            succ = True if res.returncode == 0 else False
            out, err = res.stdout, res.stderr
        except subprocess.TimeoutExpired:
            succ = False
            out, err = "", "Time limit exceeded"
        return succ, out, err

    run_success, run_stdout, run_stderr = shell_try(run_comm)

    try:
        flag_print(ansible_comm, echo=echo)
        ansible_res = subprocess.run(ansible_comm, stdout=PIPE, stderr=PIPE, text=True,
                                     timeout=TIMEOUT, shell=True)
        ansible_success = True if ansible_res.returncode == 0 else False
        ansible_stdout, ansible_stderr = ansible_res.stdout, ansible_res.stderr
    except subprocess.TimeoutExpired:
        ansible_success = False
        ansible_stdout, ansible_stderr = "", "Time limit exceeded"
    except UnicodeDecodeError:
        ansible_success = False
        ansible_stdout, ansible_stderr = "", "Unicode shenanigans"

    commit_success, commit_stdout, commit_stderr = shell_try(commit_comm)
    stop_rm_success, stop_rm_stdout, stop_rm_stderr = shell_try(stop_rm_comm)

    success = run_success and ansible_success and commit_success and stop_rm_success

    def shell_run_lines(name, comm, succ, out, err):
        return [
            log_header(f"{name} COMMAND") + f"{comm}\n\n",
            log_header(f"{name} SUCCESS") + f"{succ}\n\n",
            log_header(f"{name} STDOUT") + f"{out.strip()}\n\n",
            log_header(f"{name} STDERR") + f"{err.strip()}\n\n"
        ]

    log_path = os.path.join(LOG_DIR, image_name)
    with open(log_path, "w") as outF:
        outF.writelines(
            [log_header("IMAGE NAME") + f"{image_name}\n\n", log_header("PLAYBOOK PATH") + f"{pb_path}\n\n"] +
            shell_run_lines("RUN", run_comm, run_success, run_stdout, run_stderr) +
            shell_run_lines("ANSIBLE", ansible_comm, ansible_success, ansible_stdout, ansible_stderr) +
            shell_run_lines("COMMIT", commit_comm, commit_success, commit_stdout, commit_stderr) +
            shell_run_lines("RUN", stop_rm_comm, stop_rm_success, stop_rm_stdout, stop_rm_stderr) +
            [log_header("SUCCESS") + f"{success}\n\n"]
        )

    if success:
        return image_name
    else:
        print(f"Failed ansible - {image_name}")
        return None


def collect_test_images_worker(args: Tuple[List[str], int, bool]):
    names, idx, echo = args

    with tqdm(total=len(names), position=idx, desc=f"Loop {idx}") as pbar:
        for name in names:
            cf_image = prepare_containerfile_image(name, idx, echo)
            ans_image = prepare_ansible_image(name, idx, echo)
            time.sleep(1)
            pbar.update(1)


def collect_test_images(containerfile_names: List[str], n_proc: int):
    echo = False
    collect_test_images_worker((containerfile_names, 0, echo))

    # may return parallel execution in the future
    """
    # with multiprocessing.Pool(processes=n_proc) as pool:
        spans = parts.parts(containerfile_names, n_proc)
        pool.map(collect_ansible_diff_worker,
                 [(list(span), idx, echo) for span, idx in zip(spans, range(n_proc))])
    """


def rm_image(image: Optional[str], echo: bool):
    if image is None:
        return

    rm_comm = f"docker image rm {image}"
    rm_res = subprocess.run(["/bin/bash", "-c", rm_comm], stdout=PIPE, stderr=PIPE, text=True)
    flag_print(f"RMing {image} - stdout - {rm_res.stdout}", echo=echo)
    flag_print(f"RMing {image} - stderr - {rm_res.stderr}", echo=echo)


def diff_images_worker(image1: Optional[str], image2: Optional[str], echo: bool = True):
    log_path = os.path.join(LOG_DIR, f"diff-{image1}.json")

    if image1 is None or image2 is None:
        with open(log_path, "w") as outF:
            outF.write("[]\n")
            flag_print(f"image1: {image1}, image2: {image2}\n", echo=echo)
        return

    diff_comm = f"container-diff diff --no-cache --json --type=file daemon://{image1}:latest daemon://{image2}:latest"
    flag_print(diff_comm, echo=echo)
    diff_res = subprocess.run(['/bin/bash', '-c', diff_comm],
                              stdout=PIPE, stderr=PIPE, text=True)

    with open(log_path, "w") as outF:
        outF.write(diff_res.stdout)


def main():
    # add command to clear tmp dir
    # add command to build test stand image
    globalLog.setLevel(logging.ERROR)
    setup_dir(LOG_DIR)
    setup_dir(TMP_DIR)

    def collect():
        filenames = filenames_from_dir(GENERATOR_TESTS_DIR)
        filenames.sort()
        collect_test_images(filenames, 1)

    def diff():
        with open(GENERATOR_TEST_IMAGES_FILE, "r") as inF:
            image_hashes = [line.strip() for line in inF.readlines()]

        for image_hash in tqdm(image_hashes, desc="Collecting diff"):
            docker_image = "docker-test-" + image_hash
            ansible_image = "ansible-test-" + image_hash
            diff_images_worker(docker_image, ansible_image, echo=True)
            time.sleep(1)

    diff()


if __name__ == "__main__":
    main()
