from src.shell.main import *
from src.ansible_matcher.statistics import *
from src.ansible_matcher.command_extraction import match_extracted_call
from src.ansible_matcher.loaded_commands import *
from src.ansible_matcher.commands.command_config import *
from src.ansible_matcher.commands.template_handler import *
from src.ansible_matcher.utils import *

from src.log import globalLog


class TaskMatcher:
    stats = TaskMatcherStatistics()

    # stat flags
    collect_stats: bool = False
    stat_id: int = -1

    _tweaks: TemplateTweaks

    def match_command(self, comm: CommandCallParts, cwd: Optional[str] = None, usr: Optional[str] = None) \
            -> Optional[AnsibleTasks]:
        if cwd is None:
            cwd = "/"
        if usr is None:
            usr = "root"

        self._tweaks = TemplateTweaks(cwd=cwd, usr=usr)
        extract_res = self._extract_command_call(comm)
        if extract_res is None:
            return None
        command_name, config_cls, extracted = extract_res

        matched = self._match_extracted_call(command_name, config_cls, comm, extracted)

        # https://youtrack.jetbrains.com/issue/PY-43122/Property-is-wrongly-considered-to-be-a-callable-when-a-class-is-imported-from-a-separate-module
        # noinspection PyTypeChecker
        entry: CommandTemplateParts = config_cls.entry
        if matched is None:
            self._stat_unmatched(comm, entry)
            return None
        self._stat_matched(comm, entry)
        return matched

    def extract_command(self, comm: CommandCallParts) -> Optional[ExtractedCommandCall]:
        res = self._extract_command_call(comm)
        if res is None:
            return res
        return res[2]

    def _extract_command_call(self, comm: CommandCallParts) \
            -> Optional[Tuple[str, Type[CommandConfigABC], ExtractedCommandCall]]:

        if not TaskMatcher._check_requirements(comm):
            return None
        registry_entries = global_command_config_entry.fetch_by_command(comm)

        suitable_configs = []
        for command_name, config_cls in registry_entries:
            if config_cls.check_entry(comm):
                suitable_configs.append((command_name, config_cls))

        if not suitable_configs:
            self._stat_unknown(comm)
            return None

        if len(suitable_configs) > 1:
            globalLog.info(f"Found more than one config for {comm} - choosing one with the longest entry")
            command_name, config_cls = max(suitable_configs, key=lambda x: len(x[1].entry))
        else:
            command_name, config_cls = suitable_configs[0]

        extracted = config_cls.extract_command_call(comm)
        if extracted is None:
            self._stat_unmatched(comm, config_cls.entry)
            return None
        return command_name, config_cls, extracted

    @staticmethod
    def _check_requirements(comm: CommandCallParts) -> bool:
        return all(isinstance(part, ShellWordObject) and
                   all(isinstance(word_part, ShellParameterObject)
                       for word_part in part.parts)
                   for part in comm) \
            and comm and not comm[0].parts

    def _match_extracted_call(self, command_name: str, config_cls: Type[CommandConfigABC],
                              comm: CommandCallParts, x_call: ExtractedCommandCall) -> Optional[AnsibleTasks]:

        registry_entries = global_template_handler_registry.fetch_by_command(comm)

        for tmpl, handler, postprocess_configs, pass_opts in registry_entries:
            x_tmpl = config_cls.extract_command_template(tmpl)
            if x_tmpl is None:
                continue

            matched = match_extracted_call(x_call, x_tmpl, template_tweaks=self._tweaks)
            if matched is None:
                continue
            field_values, unmatched_opts = matched

            if pass_opts:
                handled = handler(tweaks=self._tweaks, opts=unmatched_opts, **field_values)
                if handled is None:
                    continue
                tasks, unmatched_opts = handled
            else:
                tasks = handler(tweaks=self._tweaks, **field_values)
                if tasks is None:
                    continue

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

    def _stat_unknown(self, comm: CommandCallParts) -> None:
        if not self.collect_stats:
            return
        self.stats.name.append(comm[0].value)
        self.stats.supported.append(False), self.stats.coverage.append(0.)
        line = " ".join(map(lambda x: x.value, comm))
        self.stats.length.append(len(line)), self.stats.line.append(line)
        self.stats.stat_id.append(self.stat_id)

    def _stat_unmatched(self, comm: CommandCallParts, entry: CommandTemplateParts) -> None:
        if not self.collect_stats:
            return
        self.stats.name.append(" ".join(
            map(lambda x: x.value, filter(lambda x: not x.parts, entry))
        ))
        self.stats.supported.append(True), self.stats.coverage.append(0.)
        line = " ".join(map(lambda x: x.value, comm))
        self.stats.length.append(len(line)), self.stats.line.append(line)
        self.stats.stat_id.append(self.stat_id)

    def _stat_matched(self, comm: CommandCallParts, entry: CommandTemplateParts) -> None:
        if not self.collect_stats:
            return
        self.stats.name.append(" ".join(
            map(lambda x: x.value, filter(lambda x: not x.parts, entry))
        ))
        self.stats.supported.append(True), self.stats.coverage.append(1.)
        line = " ".join(map(lambda x: x.value, comm))
        self.stats.length.append(len(line)), self.stats.line.append(line)
        self.stats.stat_id.append(self.stat_id)
