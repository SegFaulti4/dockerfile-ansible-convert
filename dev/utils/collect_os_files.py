import logging

from src.shell.bashlex.main import *
from src.containerfile.tpdockerfile.main import *
from dev.utils.data_utils import *


def os_specific_filenames(os_name: str) -> List[str]:
    shell_parser = BashlexShellParser()
    df_parser = TPDockerfileParser(shell_parser=shell_parser)
    res = []
    filenames = filenames_from_dir(CONTAINERFILES_DIR)

    for name in tqdm(filenames, desc="Collecting filenames", smoothing=1.0):
        path = os.path.join(CONTAINERFILES_DIR, name)
        try:
            with open(path.strip(), "r") as df:
                source = "".join(df.readlines())

            content = df_parser.from_str(source)
            from_directive = next(x for x in content.directives if isinstance(x, FromDirective))
            if from_directive.values[0].startswith(os_name):
                res.append(name)
        except Exception as exc:
            globalLog.info(type(exc), exc)

    return res


def main():
    os_name = "debian"
    os_dir = DEBIAN_CONTAINERFILES_DIR

    os_filenames = os_specific_filenames(os_name)
    setup_dir(os_dir)
    copy_files(list(os.path.join(CONTAINERFILES_DIR, name) for name in os_filenames), os_dir)


if __name__ == "__main__":
    globalLog.setLevel(logging.ERROR)
    main()