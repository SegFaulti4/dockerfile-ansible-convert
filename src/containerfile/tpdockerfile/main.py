from src.containerfile.tpdockerfile.transformer import *


class TPDockerfileParser(DockerfileParser):

    def __init__(self, shell_parser: ShellParser):
        self.shell_parser = shell_parser

    def parse_str(self, val: str) -> List[Tuple[Type, Dict]]:
        parsed = dockerfile.parse_string(val)
        res = []
        for cmd in parsed:
            res.append(DockerfileCommandTransformer.transform(cmd))
        return res
