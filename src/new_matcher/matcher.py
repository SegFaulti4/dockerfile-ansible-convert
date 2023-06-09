from src.new_matcher.main import *

from src.log import globalLog


class NewTaskMatcher:
    _tweaks: TemplateTweaks

    def match_command(self, comm: CommandCallParts, cwd: Optional[str] = None, usr: Optional[str] = None) \
            -> Optional[List[Dict[str, Any]]]:
        if cwd is None:
            cwd = "/"
        if usr is None:
            usr = "root"

        self._tweaks = TemplateTweaks(cwd=cwd, usr=usr)
        extract_res = self.extract_command(comm)
        if extract_res is None:
            return None
        command_name, extracted = extract_res

        matched = self._match_extracted(command_name, extracted)
        if matched is None:
            return None
        return matched

    @staticmethod
    def extract_command(comm: CommandCallParts) -> Optional[Tuple[str, ExtractedCommandCall]]:
        if not NewTaskMatcher._check_requirements(comm):
            return None
        registry_entries = global_command_config_entry.fetch_by_command(comm)
        for command_name, config_cls in registry_entries:
            extracted = config_cls.extract_command_call(comm)
            if extracted is not None:
                return command_name, extracted
        return None

    @staticmethod
    def _check_requirements(comm: CommandCallParts) -> bool:
        return all(isinstance(part, ShellWordObject) and
                   all(isinstance(word_part, ShellParameterObject)
                       for word_part in part.parts)
                   for part in comm) \
            and comm and not comm[0].parts

    def _match_extracted(self, command_name: str, extracted: ExtractedCommandCall) \
            -> Optional[List[Dict[str, Any]]]:
        raise NotImplementedError
