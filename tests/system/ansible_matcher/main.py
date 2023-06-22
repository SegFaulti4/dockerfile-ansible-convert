import subprocess
import os.path
import yaml
import time
from subprocess import PIPE

from src.ansible_matcher.main import *
from src.shell.bashlex.main import *
from tests.system.utils.data_utils import *

BASE_IMAGE = "ubuntu-test-stand"
DOCKER_NET_NAME = "test-net"


def log_header(s: str) -> str:
    return f"{s.upper()}:"


def flag_print(*args, **kwargs):
    if "echo" in kwargs and kwargs["echo"]:
        del kwargs["echo"]
        print(*args, **kwargs)


def prepare_containerfile_image(comm: str, idx: int, echo: bool = True) -> str:
    lines = [
        f"FROM {BASE_IMAGE}\n",
        f"RUN {comm}\n"
    ]
    cf_name = f"test_{idx}.Containerfile"
    cf_path = os.path.join(TMP_DIR, cf_name)
    with open(cf_path, "w") as outF:
        outF.writelines(lines)

    image_name = f"container-test-{idx}"
    build_comm = f"docker build -t {image_name} --file={cf_path} ."
    flag_print(build_comm, echo=echo)
    build_res = subprocess.run(["/bin/bash", "-c", build_comm],
                               stdout=PIPE, stderr=PIPE, text=True, timeout=210)

    log_path = os.path.join(LOG_DIR, image_name)
    with open(log_path, "w") as outF:
        outF.writelines([
            log_header("IMAGE NAME") + f"{image_name}\n\n",
            log_header("CONTAINERFILE PATH") + f"{cf_path}\n\n",
            log_header("BUILD COMMAND") + f"{build_comm}\n\n",
            log_header("BUILD STDOUT") + f"{build_res.stdout.strip()}\n\n",
            log_header("BUILD STDERR") + f"{build_res.stderr.strip()}\n\n"
        ])

    return image_name


def prepare_ansible_image(tasks: List[Dict[str, Any]], idx: int, echo: bool = True) -> str:
    plays = [
        {
            "hosts": "all",
            "tasks": tasks
        }
    ]
    pb_name = f"test_{idx}.yml"
    pb_path = os.path.join(TMP_DIR, pb_name)
    with open(pb_path, "w") as outF:
        outF.write("---\n")
        outF.write(yaml.safe_dump(plays, sort_keys=False))

    ip_addr = f"172.18.0.{idx + 2}"
    container_name = f"ansible-test-{idx}-container"
    image_name = f"ansible-test-{idx}"

    run_comm = f"docker run -d --net {DOCKER_NET_NAME} --ip {ip_addr} -p 22:22 " \
               f"--name={container_name} {BASE_IMAGE}"
    flag_print(run_comm, echo=echo)
    run_res = subprocess.run(["/bin/bash", "-c", run_comm],
                             stdout=PIPE, stderr=PIPE, text=True, timeout=210)

    time.sleep(3)
    ansible_comm = 'ansible-playbook --ssh-common-args="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" ' \
                   f'--user=root --inventory="{ip_addr}," {pb_path}'
    flag_print(ansible_comm, echo=echo)
    ansible_res = subprocess.run(['/bin/bash', '-c', ansible_comm],
                                 stdout=PIPE, stderr=PIPE, text=True, timeout=300)

    commit_comm = f"docker commit {container_name} {image_name}"
    flag_print(commit_comm, echo=echo)
    commit_res = subprocess.run(['/bin/bash', '-c', commit_comm],
                                stdout=PIPE, stderr=PIPE, text=True, timeout=300)

    stop_rm_comm = f"docker stop {container_name} && docker rm {container_name}"
    flag_print(stop_rm_comm, echo=echo)
    stop_rm_res = subprocess.run(['/bin/bash', '-c', stop_rm_comm],
                                 stdout=PIPE, stderr=PIPE, text=True, timeout=300)

    log_path = os.path.join(LOG_DIR, image_name)
    with open(log_path, "w") as outF:
        outF.writelines([
            log_header("IMAGE NAME") + f"{image_name}\n\n",
            log_header("PLAYBOOK PATH") + f"{pb_path}\n\n",
            log_header("RUN COMMAND") + f"{run_comm}\n\n",
            log_header("RUN STDOUT") + f"{run_res.stdout.strip()}\n\n",
            log_header("RUN STDERR") + f"{run_res.stderr.strip()}\n\n",
            log_header("ANSIBLE COMMAND") + f"{ansible_comm}\n\n",
            log_header("ANSIBLE STDOUT") + f"{ansible_res.stdout.strip()}\n\n",
            log_header("ANSIBLE STDERR") + f"{ansible_res.stderr.strip()}\n\n",
            log_header("COMMIT COMMAND") + f"{commit_comm}\n\n",
            log_header("COMMIT STDOUT") + f"{commit_res.stdout.strip()}\n\n",
            log_header("COMMIT STDERR") + f"{commit_res.stderr.strip()}\n\n",
            log_header("STOP RM COMMAND") + f"{stop_rm_comm}\n\n",
            log_header("STOP RM STDOUT") + f"{stop_rm_res.stdout.strip()}\n\n",
            log_header("STOP RM STDERR") + f"{stop_rm_res.stderr.strip()}\n\n"
        ])

    return image_name


def diff_images(image1: str, image2: str, echo: bool = True) -> Dict[str, Any]:
    diff_comm = f"container-diff diff --json --type=file daemon://{image1} daemon://{image2}"
    flag_print(diff_comm, echo=echo)
    diff_res = subprocess.run(['/bin/bash', '-c', diff_comm],
                              stdout=PIPE, stderr=PIPE, text=True)

    log_path = os.path.join(LOG_DIR, f"diff-{image1}-{image2}")
    with open(log_path, "w") as outF:
        outF.write(diff_res.stdout)

    return json.loads(diff_res.stdout)[0]


def run_single_test():
    # TODO: add commands for net creation somewhere
    """
    docker network rm test-net
    docker network create --subnet=172.18.0.0/16 test-net
    """

    matcher = TaskMatcher()
    parser = BashlexShellParser()

    test = "apt-get install -y --no-install-recommends curl netcat numactl"

    comm: ShellCommand = parser.parse_as_script(test).parts[0]
    tasks = matcher.match_command(comm.words, cwd='/root')

    idx = 0
    cf_image = prepare_containerfile_image(test, idx)
    ans_image = prepare_ansible_image(tasks, idx)

    diff = diff_images(cf_image, ans_image)
    print(diff)


if __name__ == "__main__":
    run_single_test()
