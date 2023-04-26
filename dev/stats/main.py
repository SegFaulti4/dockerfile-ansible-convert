import logging
import csv
import os
from collections import defaultdict
from tabulate import tabulate

from src.ansible_generator.main import *
from src.ansible_generator.statistics import *
from src.ansible_matcher.main import *
from src.ansible_matcher.statistics import *
from src.containerfile.tpdockerfile.main import *
from src.shell.bashlex.main import *
from dev.utils.data_utils import *


def tabulize_stats(stats: Union[RoleGeneratorStatistics, TaskMatcherStatistics], cut_name: bool = False):
    name_supp_coverages = defaultdict(list)
    name_supp_lengths = defaultdict(list)
    name_supp_stat_ids = defaultdict(list)

    for n, s, c, l, stat_id in zip(stats.name, stats.supported, stats.coverage, stats.length, stats.stat_id):
        name_supp_coverages[(n, s)].append(c)
        name_supp_lengths[(n, s)].append(l)
        name_supp_stat_ids[(n, s)].append(stat_id)

    headers = ["name", "supported", "usages", "occurrences", "use_coverage", "text_coverage"]
    table = []

    for n, s in name_supp_coverages:
        coverages = name_supp_coverages[(n, s)]
        lengths = name_supp_lengths[(n, s)]
        stat_ids = set(name_supp_stat_ids[(n, s)])

        usages = len(coverages)
        occurrences = len(stat_ids)
        use_coverage = sum(coverages) / usages
        text_coverage = sum(c * l for c, l in zip(coverages, lengths)) / sum(lengths)

        def cut(st: str) -> str:
            max_len = 30
            return st if len(st) < max_len else st[:max_len] + "..."

        name = cut(n) if cut_name else n
        table.append([name, s, usages, occurrences, f"{use_coverage * 100}%", f"{text_coverage * 100}%"])

    table.sort(key=lambda x: x[2], reverse=True)
    return [headers] + table


def extract_coverage_distribution(stats: TaskMatcherStatistics) -> List[float]:
    stat_id_cases = defaultdict(int)
    stat_id_coverage = defaultdict(float)
    for cov, stat_id in zip(stats.coverage, stats.stat_id):
        stat_id_cases[stat_id] += 1
        stat_id_coverage[stat_id] += cov
    res = []
    for stat_id in stat_id_cases:
        cases, coverage = stat_id_cases[stat_id], stat_id_coverage[stat_id]
        res.append(coverage / cases)
    return res


def print_containerfile_stats(generator_stats: RoleGeneratorStatistics, matcher_stats: TaskMatcherStatistics):
    generator_table = tabulize_stats(generator_stats, cut_name=True)
    matcher_table = tabulize_stats(matcher_stats, cut_name=True)

    print(tabulate(generator_table, headers='firstrow', numalign="left"))
    print()
    print(tabulate(matcher_table, headers='firstrow', numalign="left"))


def print_task_matcher_stats(matcher_stats: TaskMatcherStatistics):
    matcher_table = tabulize_stats(matcher_stats, cut_name=True)
    print(tabulate(matcher_table, headers='firstrow', numalign="left"))


def save_containerfile_stats(generator_stats: RoleGeneratorStatistics, matcher_stats: TaskMatcherStatistics,
                             stats_dir: str):
    matched_dir = os.path.join(stats_dir, "supported_commands/matched")
    unmatched_dir = os.path.join(stats_dir, "supported_commands/unmatched")

    setup_dir(stats_dir)
    setup_dir(matched_dir)
    setup_dir(unmatched_dir)

    generator_table = tabulize_stats(generator_stats)
    matcher_table = tabulize_stats(matcher_stats)
    coverage_distribution = extract_coverage_distribution(matcher_stats)

    with open(os.path.join(stats_dir, "role_generator.csv"), "w", encoding='UTF8', newline='') as outF:
        csv.writer(outF).writerows(generator_table)
    with open(os.path.join(stats_dir, "task_matcher.csv"), "w", encoding='UTF8', newline='') as outF:
        csv.writer(outF).writerows(matcher_table)
    with open(os.path.join(stats_dir, "coverage.csv"), "w", encoding='UTF8', newline='') as outF:
        csv.writer(outF).writerows([[d] for d in coverage_distribution])

    supported_matched = defaultdict(list)
    supported_unmatched = defaultdict(list)
    for name, supported, coverage, line in zip(matcher_stats.name, matcher_stats.supported,
                                               matcher_stats.coverage, matcher_stats.line):
        if not supported:
            continue
        if coverage < 1.0:
            supported_unmatched[name].append(line.strip() + "\n")
        else:
            supported_matched[name].append(line.strip() + "\n")

    for name, lines in supported_matched.items():
        with open(os.path.join(matched_dir, name), "w") as outF:
            outF.writelines(lines)
    for name, lines in supported_unmatched.items():
        with open(os.path.join(unmatched_dir, name), "w") as outF:
            outF.writelines(lines)


def collect_containerfile_stats(files_dir: str, dockerfile_parser: DockerfileParser, task_matcher: TaskMatcher)\
        -> Tuple[RoleGeneratorStatistics, TaskMatcherStatistics]:
    task_matcher.collect_stats = True
    generator_stats = RoleGeneratorStatistics()
    filenames = filenames_from_dir(files_dir)

    for stat_id, name in enumerate(tqdm(filenames, desc="Collecting stats")):
        path = os.path.join(files_dir, name)
        try:
            with open(path.strip(), "r") as df:
                source = "".join(df.readlines())

            content = dockerfile_parser.from_str(source)
            generator = RoleGenerator(tm=task_matcher, dc=content)
            task_matcher.stat_id, generator.collect_stats, generator.stat_id = stat_id, True, stat_id
            generator.generate()

            generator_stats.name.extend(generator.stats.name)
            generator_stats.supported.extend(generator.stats.supported)
            generator_stats.coverage.extend(generator.stats.coverage)
            generator_stats.length.extend(generator.stats.length)
            generator_stats.stat_id.extend(generator.stats.stat_id)

        except Exception as exc:
            globalLog.error(type(exc), exc)

    matcher_stats = task_matcher.stats
    return generator_stats, matcher_stats


def collect_task_matcher_stats(shell_parser: ShellParser, task_matcher: TaskMatcher,
                               commands_file: str) -> TaskMatcherStatistics:
    task_matcher.collect_stats = True
    with open(commands_file, "r") as inF:
        for line in tqdm(inF.readlines()):
            try:
                parsed = shell_parser.parse_as_script(line)
                comm = parsed.parts[0]
                if isinstance(comm, ShellCommandObject):
                    task_matcher.match_command(comm.parts)
            except Exception as exc:
                globalLog.info(type(exc), exc)

    matcher_stats = task_matcher.stats
    return matcher_stats


def collect_and_print_task_matcher_stats(commands_file: str):
    shell_parser = BashlexShellParser()
    task_matcher = TaskMatcher()

    matcher_stats = collect_task_matcher_stats(shell_parser, task_matcher, commands_file)
    print_task_matcher_stats(matcher_stats)


def collect_and_save_containerfile_stats(files_dir: str, stats_dir: str):
    shell_parser = BashlexShellParser()
    dockerfile_parser = TPDockerfileParser(shell_parser=shell_parser)
    task_matcher = TaskMatcher()

    generator_stats, matcher_stats = collect_containerfile_stats(files_dir, dockerfile_parser, task_matcher)
    save_containerfile_stats(generator_stats, matcher_stats, stats_dir)


def main():
    globalLog.setLevel(logging.ERROR)

    # mine_shell_commands(UBUNTU_FILES_DIR, UBUNTU_MINED_SHELL_COMMANDS_FILE)
    # collect_and_print_task_matcher_stats(os.path.join(DATA_DIR, UBUNTU_MINED_SHELL_COMMANDS_FILE))

    # commands_file = UBUNTU_MATCHER_TESTS_FILTERED_FILE
    # collect_and_print_task_matcher_stats(commands_file)

    files_dir = UBUNTU_FILES_FILTERED_DIR
    stats_dir = os.path.join(UBUNTU_DATA_DIR, "stats_filtered")
    collect_and_save_containerfile_stats(files_dir, stats_dir)


if __name__ == "__main__":
    globalLog.setLevel(logging.ERROR)
    main()
