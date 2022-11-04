from src.dockerfile.tpdockerfile.transformer import *


class TPDockerfileParser(DockerfileParser):

    def parse_str(self, val: str) -> List[Tuple[Type, Dict]]:
        parsed = dockerfile.parse_string(val)
        res = []
        for cmd in parsed:
            res.append(DockerfileCommandTransformer.transform(cmd))
        return res
