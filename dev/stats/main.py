import logging
from collections import defaultdict
from tabulate import tabulate
from tqdm import tqdm

from src.ansible_generator.main import *
from src.ansible_generator.statistics import *
from src.ansible_matcher.example_based.main import *
from src.ansible_matcher.example_based.statistics import *
from src.containerfile.tpdockerfile.main import *
from src.shell.bashlex.main import *
from dev.utils.file_utils import *


def tabulize_stats(stats: Union[RoleGeneratorStatistics, ExampleBasedMatcherStatistics]):
    name_coverages = defaultdict(list)
    name_lengths = defaultdict(list)

    for n, c, l in zip(stats.names, stats.coverages, stats.lengths):
        name_coverages[n].append(c)
        name_lengths[n].append(l)

    headers = ["name", "cases", "case_coverage", "text_coverage"]
    table = []

    for n in name_coverages:
        coverages = name_coverages[n]
        lengths = name_lengths[n]

        count = len(coverages)
        case_coverage = sum(coverages) / count
        text_coverage = sum(c * l for c, l in zip(coverages, lengths)) / sum(lengths)

        def cut(s: str) -> str:
            max_len = 30
            return s if len(s) < max_len else s[:max_len] + "..."

        table.append([cut(n), count, f"{case_coverage * 100}%", f"{text_coverage * 100}%"])

    table.sort(key=lambda x: x[1], reverse=True)

    return [headers] + table


if __name__ == "__main__":
    globalLog.setLevel(logging.WARNING)

    shell_parser = BashlexShellParser()
    dockerfile_parser = TPDockerfileParser(shell_parser=shell_parser)
    task_matcher = ExampleBasedMatcher()
    generator_stats = RoleGeneratorStatistics()

    #extract_containerfiles()
    filenames = filenames_from_dir(CONTAINERFILES_DIR)
    for i, name in tqdm(enumerate(filenames), desc="Collecting stats"):
        if i % 10000 == 9999:
            print()

        path = os.path.join(CONTAINERFILES_DIR, name)
        try:
            with open(path.strip(), "r") as df:
                source = "".join(df.readlines())

            content = dockerfile_parser.from_str(source)
            generator = RoleGenerator(tm=task_matcher, dc=content)
            role = generator.generate()

            #generator_stats.names.extend(generator.stats.names)
            #generator_stats.coverages.extend(generator.stats.coverages)
            #generator_stats.lengths.extend(generator.stats.lengths)

        except Exception as exc:
            pass
            # globalLog.warning(type(exc), exc)

    matcher_stats = task_matcher.stats

    generator_table = tabulize_stats(generator_stats)
    matcher_table = tabulize_stats(matcher_stats)

    print(tabulate(generator_table, headers='firstrow', numalign="left"))
    print()
    print(tabulate(matcher_table, headers='firstrow', numalign="left"))
