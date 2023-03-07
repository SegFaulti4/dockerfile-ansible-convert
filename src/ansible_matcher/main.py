import copy
from typing import Union, Any

from src.ansible_matcher.template_lang import \
    TemplatePart, TemplateMatchResult, TemplateTweaks, TemplateFiller
from src.ansible_matcher.commands import *
from src.ansible_matcher.opts_extraction import \
    ExtractedCommandCall, ExtractedCommandTemplate, CommandOptsExtractor
from src.ansible_matcher.utils import visit_dict, merge_dicts, listify
from src.ansible_matcher.statistics import *


class TaskMatcher:
    stats = TaskMatcherStatistics()

    _tweaks: TemplateTweaks
    _config_loader: CommandConfigLoader

    def __init__(self, config_loader: CommandConfigLoader = init_command_config_loader):
        self._config_loader = config_loader

    def match_command(self, comm: CommandCallParts, cwd: Optional[str] = None, usr: Optional[str] = None,
                      collect_stats: bool = False) \
            -> Union[Dict[str, Any], None]:
        if not TaskMatcher._check_requirements(comm):
            return None

        command_config = self._config_loader.load(comm)
        if command_config is None:
            self._stat_unknown(comm, collect_stats)
            return None

        self._tweaks = TemplateTweaks(cwd=cwd, usr=usr)

        extracted_call = TaskMatcher._extract_command_call(command_config, comm)
        if extracted_call is None:
            self._stat_unmatched(comm, command_config, collect_stats)
            return None

        for command_template, task_template in command_config.examples:
            task_call = self._match_template(command_config, command_template,
                                             extracted_call, task_template)
            if task_call is None:
                continue

            self._stat_matched(comm, command_config, collect_stats)
            return task_call

        self._stat_unmatched(comm, command_config, collect_stats)
        return None

    def extract_command(self, comm: CommandCallParts) -> Optional[ExtractedCommandCall]:
        if not TaskMatcher._check_requirements(comm):
            return None

        command_config = self._config_loader.load(comm)
        if command_config is None:
            return None

        extracted_call = TaskMatcher._extract_command_call(command_config, comm)
        return extracted_call

    def _stat_unknown(self, comm: CommandCallParts, collect_stat: bool) -> None:
        if not collect_stat:
            return
        self.stats.name.append(comm[0].value)
        self.stats.supported.append(False)
        self.stats.coverage.append(0.)
        line = " ".join(map(lambda x: x.value, comm))
        self.stats.length.append(len(line))
        self.stats.line.append(line)

    def _stat_unmatched(self, comm: CommandCallParts, command_config: CommandConfig, collect_stat: bool) -> None:
        if not collect_stat:
            return
        self.stats.name.append(" ".join(
            map(lambda x: x.value, filter(lambda x: not x.parts, command_config.entry))
        ))
        self.stats.supported.append(True)
        self.stats.coverage.append(0.)
        line = " ".join(map(lambda x: x.value, comm))
        self.stats.length.append(len(line))
        self.stats.line.append(line)

    def _stat_matched(self, comm: CommandCallParts, command_config: CommandConfig, collect_stat: bool) -> None:
        if not collect_stat:
            return
        self.stats.name.append(" ".join(
            map(lambda x: x.value, filter(lambda x: not x.parts, command_config.entry))
        ))
        self.stats.supported.append(True)
        self.stats.coverage.append(1.)
        line = " ".join(map(lambda x: x.value, comm))
        self.stats.length.append(len(line))
        self.stats.line.append(line)

    @staticmethod
    def _check_requirements(comm: CommandCallParts) -> bool:
        return all(isinstance(part, ShellWordObject) and
                   all(isinstance(word_part, ShellParameterObject)
                       for word_part in part.parts)
                   for part in comm) \
            and comm and not comm[0].parts

    @staticmethod
    def _extract_command_call(command_config: CommandConfig, comm: CommandCallParts) \
            -> Optional[ExtractedCommandCall]:

        opts_extractor = CommandOptsExtractor(opts_map=command_config.opts)
        tmp = copy.deepcopy(comm)
        return opts_extractor.extract(tmp)

    def _match_template(self, command_config: CommandConfig, command_template: CommandTemplateParts,
                        extracted_call: ExtractedCommandCall, example_task_template: Dict[str, Any]) \
            -> Optional[Dict[str, Any]]:

        extracted_template = TaskMatcher._extract_command_template(command_config, command_template)
        if extracted_template is None:
            return None

        match_result = self.match_extracted_template(extracted_call, extracted_template)
        if match_result is None:
            return None
        parameter_fields, unmatched_opts = match_result

        postprocess_res = self._postprocess_opts(command_config, unmatched_opts)
        if postprocess_res is None:
            return None
        opt_fields, postprocess_task_template = postprocess_res
        fields_dict = CommandTemplateMatcher.merge_match_results(parameter_fields, opt_fields)

        # needed for referencing current working directory
        fields_dict = self._merge_special_fields(fields_dict)

        task_template = TaskMatcher._merge_task_templates(example_task_template,
                                                          postprocess_task_template)
        task_call = TaskMatcher._fill_in_task_template(task_template, fields_dict)
        if task_call is None:
            return None

        return task_call

    @staticmethod
    def _extract_command_template(command_config: CommandConfig, templ: CommandTemplateParts) \
            -> Optional[ExtractedCommandTemplate]:

        opts_extractor = CommandOptsExtractor(opts_map=command_config.opts)
        tmp = copy.deepcopy(templ)
        return opts_extractor.extract(tmp)

    def match_extracted_template(self, ext_call: ExtractedCommandCall, ext_templ: ExtractedCommandTemplate) \
            -> Optional[Tuple[TemplateMatchResult, Dict[str, CommandCallParts]]]:

        params_matcher = CommandTemplateMatcher(template=ext_templ.params, template_tweaks=self._tweaks)
        param_fields = params_matcher.full_match(ext_call.params)
        if param_fields is None:
            return None

        opt_match = self.match_opts(ext_call.opts, ext_templ.opts)
        if opt_match is None:
            return None
        opt_fields, unmatched_opts = opt_match

        fields_dict = CommandTemplateMatcher.merge_match_results(param_fields, opt_fields)
        return fields_dict, unmatched_opts

    def match_opts(self, call_opts: Dict[str, CommandCallParts], templ_opts: Dict[str, CommandTemplateParts]) \
            -> Optional[Tuple[TemplateMatchResult, Dict[str, CommandCallParts]]]:

        opt_fields = dict()
        unmatched_opts = {k: listify(v) for k, v in call_opts.items()}

        for k, v in templ_opts.items():
            if k not in call_opts:
                return None
            v = listify(v)

            if not v and not unmatched_opts[k]:
                del unmatched_opts[k]
                continue
            if not v or not unmatched_opts[k]:
                return None

            opt_matcher = CommandTemplateMatcher(template=v, template_tweaks=self._tweaks)
            opt_match = opt_matcher.match(call_opts[k])
            if opt_match is None:
                return None
            tmp_fields, unmatched = opt_match

            opt_fields = CommandTemplateMatcher.merge_match_results(opt_fields, tmp_fields)
            if not unmatched:
                del unmatched_opts[k]
            else:
                unmatched_opts[k] = unmatched

        return opt_fields, unmatched_opts

    def _postprocess_opts(self, command_config: CommandConfig, opts_dict: Dict[str, CommandCallParts]) \
            -> Optional[Tuple[TemplateMatchResult, Dict[str, Any]]]:

        fields_dict = dict()
        task_template = dict()
        for opt_template, opt_task_template in command_config.opts_postprocess:
            ext_opt_templ = TaskMatcher._extract_command_template(command_config, opt_template)
            if ext_opt_templ is None:
                continue

            opt_match = self.match_opts(opts_dict, ext_opt_templ.opts)
            if opt_match is None:
                continue
            opt_fields, unmatched_opts = opt_match

            fields_dict = CommandTemplateMatcher.merge_match_results(fields_dict, opt_fields)
            opts_dict = unmatched_opts
            task_template = TaskMatcher._merge_task_templates(task_template, opt_task_template)

        if opts_dict:
            return None
        return fields_dict, task_template

    @staticmethod
    def _fill_in_task_template(task_template: Dict[str, Any], fields_dict: TemplateMatchResult) \
            -> Optional[Dict[str, Any]]:

        class TaskTemplateFiller:
            def __init__(self, f_dict: TemplateMatchResult):
                self.fields_dict = f_dict
                self.success = True

            def __call__(self, templ: CommandTemplateParts):
                if not self.success:
                    return ""

                template_filler = TemplateFiller(templ)
                res = template_filler.fill(self.fields_dict)
                if res is None:
                    self.success = False
                    return ""
                return res

        def is_template(x) -> bool:
            return isinstance(x, list) and all(isinstance(y, TemplatePart) for y in x)

        filler = TaskTemplateFiller(fields_dict)
        task_call = visit_dict(task_template, is_template, filler)
        if not filler.success:
            return None
        return task_call

    @staticmethod
    def _merge_task_templates(into_templ: Dict[str, Any], from_templ: Dict[str, Any]) -> Dict[str, Any]:
        tmp = copy.deepcopy(into_templ)
        return merge_dicts(tmp, from_templ)

    def _merge_special_fields(self, fields_dict: TemplateMatchResult) -> TemplateMatchResult:
        if self._tweaks.cwd is not None:
            fields_dict["cwd"] = self._tweaks.cwd
        return fields_dict
