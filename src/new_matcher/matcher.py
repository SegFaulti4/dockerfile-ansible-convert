from src.new_matcher.main import *


class NewTaskMatcher:
    _tweaks: TemplateTweaks

    def match_command(self, comm: CommandCallParts, cwd: Optional[str] = None, usr: Optional[str] = None) \
            -> Optional[AnsibleTasks]:
        if cwd is None:
            cwd = "/"
        if usr is None:
            usr = "root"

        self._tweaks = TemplateTweaks(cwd=cwd, usr=usr)
        extract_res = self.extract_command_call(comm)
        if extract_res is None:
            return None
        command_name, config_cls, extracted = extract_res

        matched = self._match_extracted_call(command_name, config_cls, comm, extracted)
        if matched is None:
            return None
        return matched

    @staticmethod
    def extract_command(comm: CommandCallParts) -> Optional[ExtractedCommandCall]:
        res = NewTaskMatcher.extract_command_call(comm)
        if res is None:
            return res
        return res[2]

    @staticmethod
    def extract_command_call(comm: CommandCallParts) -> Optional[Tuple[str, Type[CommandConfig], ExtractedCommandCall]]:
        if not NewTaskMatcher._check_requirements(comm):
            return None
        registry_entries = global_command_config_entry.fetch_by_command(comm)
        for command_name, config_cls in registry_entries:
            extracted = config_cls.extract_command_call(comm)
            if extracted is not None:
                return command_name, config_cls, extracted
        return None

    @staticmethod
    def _check_requirements(comm: CommandCallParts) -> bool:
        return all(isinstance(part, ShellWordObject) and
                   all(isinstance(word_part, ShellParameterObject)
                       for word_part in part.parts)
                   for part in comm) \
            and comm and not comm[0].parts

    def _match_extracted_call(self, command_name: str, config_cls: Type[CommandConfig],
                              comm: CommandCallParts, x_call: ExtractedCommandCall) -> Optional[AnsibleTasks]:

        registry_entries = global_template_handler_registry.fetch_by_command(comm)

        for tmpl, handler, postprocess_configs in registry_entries:
            x_tmpl = config_cls.extract_command_template(tmpl)
            if x_tmpl is None:
                continue

            matched = match_extracted_call(x_call, x_tmpl, template_tweaks=self._tweaks)
            if matched is None:
                continue
            field_values, unmatched_opts = matched

            tasks = handler(tweaks=self._tweaks, **field_values)

            if command_name in postprocess_configs:
                extra_params, unmatched_pp_opts = \
                    config_cls.postprocess_command_opts(unmatched_opts, tweaks=self._tweaks)
                if unmatched_pp_opts:
                    continue
            else:
                extra_params = dict()

            self._merge_extra_parameters(tasks, extra_params)
            return tasks

        return None

    @staticmethod
    def _merge_extra_parameters(tasks: AnsibleTasks, extra_params: Dict[str, Any]) -> None:
        for task in tasks:
            for key in filter(lambda x: x in extra_params, task):
                task[key] = merge_dicts(task[key], extra_params[key], override=True)


def main():
    filepath = "/home/popovms/course/dev/sandbox/ansible_matcher/input"
    commands = []
    with open(filepath, "r") as inF:
        commands.extend([line.strip() for line in inF.readlines()])

    print()


if __name__ == "__main__":
    main()
