import yaml
import subprocess
from typing import Any, List, Dict

import sandbox.utils.file_utils as file_utils


def write_new_role(role_name: str, tasks: List[Dict[str, Any]]) -> None:
    role_tasks_path = f"{file_utils.SANDBOX_DIR}/ansible/roles/{role_name}/tasks"
    file_utils.setup_dir(role_tasks_path)

    with open(f"{role_tasks_path}/main.yml", "w") as outF:
        yaml.dump(tasks, outF)


def execute_role(role_name: str, host_ip: str, ansible_ssh_user: str) -> None:
    command = ["ansible", "all",
               "-i", f"'{host_ip}'",
               "-u", f"{ansible_ssh_user}",
               "-m", "include_role",
               "-a", f"name={role_name}"]
    ansible_wd = f"file_utils.SANDBOX_DIR/ansible"
    p = subprocess.Popen(command, cwd=ansible_wd)
    p.wait()
