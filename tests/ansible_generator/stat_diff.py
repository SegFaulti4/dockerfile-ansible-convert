import glob
import json
import os
import os.path

from tests.utils.data_utils import *

diff_dir = "/home/popovms/course/tests/data/log/"
diff_glob = os.path.join(diff_dir, "diff-docker-test-*.json")
# diff_dir = "/home/popovms/course/tests/data/filtered_diff_backup"
# diff_glob = os.path.join(diff_dir, "*.json")
diff_files = list(glob.glob(diff_glob))
diff_files.sort()

filtered_diff_dir = "/home/popovms/course/tests/data/filtered_diff"

file_prefix_blacklist = [
    # from adds
    '/root/.ansible',
    '/root/.cache',
    '/run/motd.dynamic',
    '/usr/lib/python3/dist-packages/__pycache__',
    '/usr/lib/python3/dist-packages/apt',
    '/usr/lib/python3/dist-packages/python_apt',
    '/usr/share/doc/python-apt',
    '/usr/share/doc/python3-apt',
    '/usr/share/lintian/overrides/python3-apt',
    '/usr/share/python-apt',
    '/var/lib/dpkg/info/python-apt',
    '/var/lib/dpkg/info/python3-apt',
    # from mods
    '/var/log/dpkg',
    '/var/log/apt',
    '/var/log/lastlog',
    '/var/log/wtmp',
    '/var/cache/ldconfig/aux-cache',  # (this one is pretty suspicious) actually it is not even changed between images
    '/var/log/apt/eipp.log.xz',
    '/var/lib/apt/extended_states',  # (this one is somewhat suspicious) probably because of apt instead of apt-get
    '/var/lib/dpkg/status',  # (this one is somewhat suspicious) same
    '/run/sshd.pid',
    '/var/log/alternatives.log',
    # anything with .ansible

    # temporarily ignored
    '/root/.wget-hsts',
    '/etc/passwd',
    '/etc/passwd-',
    '/etc/shadow',
    '/var/cache/debconf/config.dat',
    '/etc/localtime',
    '/etc/timezone'
]
file_prefix_same_size_mod_blacklist = [
    '/var/lib/apt-cacher-ng/backends_ubuntu.default',
    '/root/miniconda3/lib/python3.6/__pycache__',
    '/var/lib/mysql/',
    '/etc/mysql/debian.cnf',
    '/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_jammy',
    '/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_jammy',
    '/var/lib/apt/lists/mirrors.ubuntu.com_mirrors.txt_dists_jammy',
    '/usr/local/lib/python3.10/dist-packages',
    '/var/www/wailer/venv/lib/python3.9/site-packages/ansible_collections'
]

add_counts = dict()
delete_counts = dict()
mod_counts = dict()

add_names = dict()
delete_names = dict()
mod_names = dict()

single_adds, single_add_names = [], []
single_deletes, single_delete_names = [], []
single_mods, single_mod_names = [], []

add_uniques = set()
delete_uniques = set()
mod_uniques = set()
all_uniques = set()


def save_filtered_diffs():
    setup_dir(filtered_diff_dir)

    def filter_diff(diff_list):
        if diff_list is None:
            return []

        res = [d for d in diff_list if not any(d["Name"].startswith(prefix) for prefix in file_prefix_blacklist)]
        return res

    def filter_ansible_files(diff_list):
        if diff_list is None:
            return []

        res = [d for d in diff_list if '.ansible' not in d["Name"]]
        return res

    def filter_same_size_mods(mods):
        if mods is None:
            return []

        res = [d for d in mods if d["Size1"] != d["Size2"] or
               not any(d["Name"].startswith(prefix) for prefix in file_prefix_same_size_mod_blacklist)]
        return res

    for diff_file in diff_files:
        with open(diff_file, "r") as inF:
            diff_arr = json.load(inF)

        image_hash = diff_arr[0]["Image1"][12:-7]
        out_filename = image_hash + ".json"
        for diff in diff_arr:
            diff["Diff"]["Adds"] = filter_diff(diff["Diff"]["Adds"])
            diff["Diff"]["Dels"] = filter_diff(diff["Diff"]["Dels"])
            diff["Diff"]["Mods"] = filter_diff(diff["Diff"]["Mods"])

            diff["Diff"]["Adds"] = filter_ansible_files(diff["Diff"]["Adds"])
            diff["Diff"]["Dels"] = filter_ansible_files(diff["Diff"]["Dels"])
            diff["Diff"]["Mods"] = filter_ansible_files(diff["Diff"]["Mods"])

            diff["Diff"]["Mods"] = filter_same_size_mods(diff["Diff"]["Mods"])

        if all(not diff["Diff"]["Adds"] and not diff["Diff"]["Dels"] and not diff["Diff"]["Mods"]
               for diff in diff_arr):
            continue
        else:
            print()

        with open(os.path.join(filtered_diff_dir, out_filename), "w") as outF:
            json.dump(diff_arr, outF, indent=4, sort_keys=True)


def collect_filtered_adm_names_counts():
    global diff_files
    diff_files = [os.path.join(filtered_diff_dir, f) for f in os.listdir(filtered_diff_dir)
                  if os.path.isfile(os.path.join(filtered_diff_dir, f))]
    diff_files.sort()
    collect_adm_names_counts()


def collect_adm_names_counts():
    for diff_file in diff_files:
        with open(diff_file, "r") as inF:
            diff_arr = json.load(inF)
        for diff in diff_arr:
            d_image = diff["Image1"]
            # a_image = diff["Image2"]
            adds = diff["Diff"]["Adds"]
            deletes = [] if diff["Diff"]["Dels"] is None else diff["Diff"]["Dels"]
            mods = diff["Diff"]["Mods"]

            for add in (x["Name"] for x in adds):
                if add not in add_counts:
                    add_counts[add] = 0
                add_counts[add] += 1
                if add not in add_names:
                    add_names[add] = []
                add_names[add].append(d_image)

            for delete in (x["Name"] for x in deletes):
                if delete not in delete_counts:
                    delete_counts[delete] = 0
                delete_counts[delete] += 1
                if delete not in delete_names:
                    delete_names[delete] = []
                delete_names[delete].append(d_image)

            for mod in (x["Name"] for x in mods):
                if mod not in mod_counts:
                    mod_counts[mod] = 0
                mod_counts[mod] += 1
                if mod not in mod_names:
                    mod_names[mod] = []
                mod_names[mod].append(d_image)


def delete_adm_blacklist_files():
    global add_counts, add_names, delete_counts, delete_names, mod_counts, mod_names

    def func(counts, names):
        for prefix in file_prefix_blacklist:
            for_delete = [file for file in counts if file.startswith(prefix)]
            for k in for_delete:
                del counts[k]
                del names[k]
        return counts, names

    add_counts, add_names = func(add_counts, add_names)
    delete_counts, delete_names = func(delete_counts, delete_names)
    mod_counts, mod_names = func(mod_counts, mod_names)


def collect_adm_singles():
    single_adds.extend([k for k in add_counts if add_counts[k] == 1])
    single_add_names.extend(list(set(names for k in single_adds for names in add_names[k])))
    single_deletes.extend([k for k in delete_counts if delete_counts[k] == 1])
    single_delete_names.extend(list(set(names for k in single_deletes for names in delete_names[k])))
    single_mods.extend([k for k in mod_counts if mod_counts[k] == 1])
    single_mod_names.extend(list(set(names for k in single_mods for names in mod_names[k])))


def collect_adm_uniques():
    global add_uniques, delete_uniques, mod_uniques, all_uniques
    for n in add_names.values():
        add_uniques = add_uniques | set(n)
    for n in delete_names.values():
        delete_uniques = delete_uniques | set(n)
    for n in mod_names.values():
        mod_uniques = mod_uniques | set(n)
    all_uniques = add_uniques | delete_uniques | mod_uniques

    add_uniques = list(add_uniques)
    delete_uniques = list(delete_uniques)
    mod_uniques = list(mod_uniques)
    all_uniques = list(all_uniques)

    add_uniques.sort(), mod_uniques.sort(), delete_uniques.sort(), all_uniques.sort()


def print_adm_singles():
    print(f"single adds: {len(single_add_names)}")
    print(*single_add_names, sep='\n')
    print(f"single deletes: {len(single_delete_names)}")
    print(*single_delete_names, sep='\n')
    print(f"single mods: {len(single_mod_names)}")
    print(*single_mod_names, sep='\n')


def print_adm_uniques():
    print(f"add uniques: {len(add_uniques)}")
    print(*add_uniques, sep='\n')
    print(f"delete uniques: {len(delete_uniques)}")
    print(*delete_uniques, sep='\n')
    print(f"mod uniques: {len(mod_uniques)}")
    print(*mod_uniques, sep='\n')
    print(f"all uniques: {len(all_uniques)}")
    print(*all_uniques, sep='\n')


def print_adm():
    print(f"adds: {len(add_counts)}")
    print(*add_counts.keys(), sep='\n')
    print(f"deletes: {len(delete_counts)}")
    print(*delete_counts.keys(), sep='\n')
    print(f"mods: {len(mod_counts)}")
    print(*mod_counts.keys(), sep='\n')


if __name__ == "__main__":
    # save_filtered_diffs()
    collect_filtered_adm_names_counts()

    # collect_adm_names_counts(), delete_adm_blacklist_files()

    collect_adm_singles(), print_adm_singles()
    # collect_adm_uniques(), print_adm_uniques()
    print_adm()

    print()
