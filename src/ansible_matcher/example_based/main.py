import copy
from typing import Union, Optional, Dict, Any, Type, Callable

from src.ansible_matcher.main import *
from src.ansible_matcher.example_based.template_lang import \
    CommandCallParts, CommandTemplateParts, TemplatePart, TemplateField, \
    TemplateMatchResult, CommandTemplateMatcher, TemplateTweaks, TemplateFiller
from src.ansible_matcher.example_based.commands import CommandConfig, command_config_loader
from src.ansible_matcher.example_based.opts_extraction import \
    ExtractedCommandCall, ExtractedCommandTemplate, CommandOptsExtractor
from src.ansible_matcher.example_based.utils import visit_dict, merge_dicts

from src.log import globalLog


class ExampleBasedMatcher(TaskMatcher):
    _tweaks: TemplateTweaks
    _config_loader = command_config_loader

    def __init__(self):
        pass

    def match_command(self, comm: CommandCallParts, cwd: Optional[str] = None, usr: Optional[str] = None) \
            -> Union[Dict[str, Any], None]:
        if not ExampleBasedMatcher.check_requirements(comm):
            return None

        command_config = self._config_loader.load(comm)
        if command_config is None:
            return None

        self._tweaks = TemplateTweaks(cwd=cwd, usr=usr)

        extracted_call = ExampleBasedMatcher.extract_command_call(command_config, comm)
        if extracted_call is None:
            return None

        for command_template, task_template in command_config.examples:
            task_call = self.match_template(command_config, command_template,
                                                           extracted_call, task_template)
            if task_call is None:
                continue
            return task_call

        return None

    @staticmethod
    def check_requirements(comm: CommandCallParts) -> bool:
        return all(isinstance(part, ShellWordObject) and
                   all(isinstance(word_part, ShellParameterObject)
                       for word_part in part.parts)
                   for part in comm) \
               and comm and not comm[0].parts

    @staticmethod
    def extract_command_call(command_config: CommandConfig, comm: CommandCallParts) \
            -> Optional[ExtractedCommandCall]:

        opts_extractor = CommandOptsExtractor(opts_map=command_config.opts)
        tmp = copy.deepcopy(comm)
        return opts_extractor.extract(tmp)

    def match_template(self, command_config: CommandConfig, command_template: CommandTemplateParts,
                       extracted_call: ExtractedCommandCall, example_task_template: Dict[str, Any]) \
            -> Optional[Dict[str, Any]]:

        extracted_template = ExampleBasedMatcher.extract_command_template(command_config, command_template)
        if extracted_template is None:
            return None

        match_result = self.match_extracted_template(extracted_call, extracted_template)
        if match_result is None:
            return None
        parameter_fields, unmatched_opts = match_result

        postprocess_res = self.postprocess_opts(command_config, unmatched_opts)
        if postprocess_res is None:
            return None
        opt_fields, postprocess_task_template = postprocess_res
        fields_dict = CommandTemplateMatcher.merge_match_results(parameter_fields, opt_fields)

        task_template = ExampleBasedMatcher.merge_task_templates(postprocess_task_template,
                                                                 copy.deepcopy(example_task_template))
        task_call = ExampleBasedMatcher.fill_in_task_template(task_template, fields_dict)
        if task_call is None:
            return None

        return task_call

    @staticmethod
    def extract_command_template(command_config: CommandConfig, templ: CommandTemplateParts) \
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
        unmatched_opts = dict()
        for k, v in templ_opts.items():
            if k not in call_opts:
                return None
            if v is None:
                continue
            if call_opts[k] is None:
                return None

            opt_matcher = CommandTemplateMatcher(template=v, template_tweaks=self._tweaks)
            opt_match = opt_matcher.match(call_opts[k])
            if opt_match is None:
                return None
            tmp_fields, unmatched = opt_match

            opt_fields = CommandTemplateMatcher.merge_match_results(opt_fields, tmp_fields)
            if unmatched:
                unmatched_opts[k] = unmatched

        return opt_fields, unmatched_opts

    def postprocess_opts(self, command_config: CommandConfig, opts_dict: Dict[str, CommandCallParts]) \
            -> Optional[Tuple[TemplateMatchResult, Dict[str, Any]]]:

        fields_dict = dict()
        task_template = dict()
        for opt_template, opt_task_template in command_config.opts_postprocess:
            ext_opt_templ = ExampleBasedMatcher.extract_command_template(command_config, opt_template)
            if ext_opt_templ is None:
                continue

            opt_match = self.match_opts(opts_dict, ext_opt_templ.opts)
            if opt_match is None:
                continue
            opt_fields, unmatched_opts = opt_match

            fields_dict = CommandTemplateMatcher.merge_match_results(fields_dict, opt_fields)
            opts_dict = unmatched_opts
            task_template = ExampleBasedMatcher.merge_task_templates(task_template, opt_task_template)

        if opts_dict:
            return None
        return fields_dict, task_template

    @staticmethod
    def fill_in_task_template(task_template: Dict[str, Any], fields_dict: TemplateMatchResult) \
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
    def merge_task_templates(into_templ: Dict[str, Any], from_templ: Dict[str, Any]) -> Dict[str, Any]:
        return merge_dicts(into_templ, from_templ)
