import dataclasses
import json
import glob
import os
from typing import Optional, Dict

from src.shell.main import *
from src.ansible_matcher.example_based.template_lang import \
    CommandCallParts, CommandTemplateParts, \
    TemplateConstructor, CommandTemplateMatcher
from src.ansible_matcher.example_based.opts_extraction import CommandOpt
from src.ansible_matcher.example_based.utils import visit_dict

from src.log import globalLog


@dataclasses.dataclass
class CommandConfig:
    entry: CommandTemplateParts
    examples: List[Tuple[CommandTemplateParts, Dict]]
    opts: Dict[str, CommandOpt]
    opts_postprocess: List[Tuple[CommandTemplateParts, Dict]]


class CommandConfigLoader:

    def load(self, comm: CommandCallParts) -> Optional[CommandConfig]:
        raise NotImplementedError


class JsonCommandConfigLoader:
    _configs: List[CommandConfig]

    ENTRY = "entry"
    EXAMPLES = "examples"
    OPTS = "opts"
    OPTS_POSTPROCESS = "opts_postprocess"

    OPT_ALIASES = "aliases"
    OPT_ARG_REQUIRED = "arg_required"
    OPT_MANY_ARGS = "many_args"

    def __init__(self):
        self._configs = []
        commands_glob = os.path.join(os.path.dirname(__file__), "commands/*.json")

        for path in glob.glob(commands_glob):
            configs = JsonCommandConfigLoader._load_config_from_json(path)
            self._configs.extend(configs)

    def load(self, comm: CommandCallParts) -> Optional[CommandConfig]:
        for config in self._configs:
            if JsonCommandConfigLoader._check_entry(config, comm):
                return config
        return None

    @staticmethod
    def _check_entry(config: CommandConfig, comm: CommandCallParts) -> bool:
        matcher = CommandTemplateMatcher(template=config.entry)
        match = matcher.full_match(comm)

        if match is None:
            return False
        return True

    @staticmethod
    def _create_comm_templ(comm: str) -> Optional[CommandTemplateParts]:
        comm_templ = TemplateConstructor().from_str(comm)

        if comm_templ is None:
            globalLog.warn("Failed to create command template")
            return None

        return comm_templ

    @staticmethod
    def _create_task_template(task: Dict) -> Optional[Dict]:

        class TaskTemplater:
            def __init__(self):
                self.success = True

            def __call__(self, s: str):
                if not self.success:
                    return ""

                new_s = TemplateConstructor().from_str(s)
                if new_s is None:
                    self.success = False
                    return ""
                return new_s

        templater = TaskTemplater()
        task_templ = visit_dict(task, lambda x: isinstance(x, str), templater)

        if not templater.success:
            globalLog.warn("Failed to create task template")
            return None

        return task_templ

    @staticmethod
    def _load_entry(entry: Optional[str]) -> Optional[CommandTemplateParts]:
        if entry is None or not isinstance(entry, str):
            globalLog.warn(f"Command config '{JsonCommandConfigLoader.ENTRY}' is not set properly")
            return None

        return JsonCommandConfigLoader._create_comm_templ(entry)

    @staticmethod
    def _load_examples(examples: Optional[Dict[str, Dict]]) -> Optional[List[Tuple[CommandTemplateParts, Dict]]]:
        if examples is None or not isinstance(examples, dict):
            globalLog.warn(f"Command config '{JsonCommandConfigLoader.EXAMPLES}' is not set properly")
            return None

        res = []
        for comm, task in examples.items():
            if not isinstance(comm, str):
                globalLog.warn(f"Wrong type of command template in '{JsonCommandConfigLoader.EXAMPLES}'")
                continue
            if not isinstance(task, dict):
                globalLog.warn(f"Wrong type of task template in '{JsonCommandConfigLoader.EXAMPLES}'")
                continue

            comm_templ = JsonCommandConfigLoader._create_comm_templ(comm)
            if comm_templ is None:
                continue
            task_templ = JsonCommandConfigLoader._create_task_template(task)
            if task_templ is None:
                continue

            res.append((comm_templ, task_templ))

        return res

    @staticmethod
    def _load_opts(opts: Dict) -> Optional[Dict[str, CommandOpt]]:
        if opts is None or not isinstance(opts, dict):
            globalLog.warn(f"Command config '{JsonCommandConfigLoader.OPTS}' is not set properly")
            return None

        res = dict()
        for opt_name, opt in opts.items():
            if not isinstance(opt_name, str):
                globalLog.warn(f"Wrong type of option name in '{JsonCommandConfigLoader.OPTS}'")
                continue
            if not isinstance(opt, Dict):
                globalLog.warn(f"Wrong type of option config in '{JsonCommandConfigLoader.OPTS}'")
                continue

            if JsonCommandConfigLoader.OPT_ALIASES not in opt \
                    or JsonCommandConfigLoader.OPT_ARG_REQUIRED not in opt \
                    or JsonCommandConfigLoader.OPT_MANY_ARGS not in opt:
                globalLog.warn(f"Option {opt_name} config is incomplete")
                continue

            aliases = opt[JsonCommandConfigLoader.OPT_ALIASES]
            arg_required = opt[JsonCommandConfigLoader.OPT_ARG_REQUIRED]
            many_args = opt[JsonCommandConfigLoader.OPT_MANY_ARGS]

            if not isinstance(aliases, list) or any(not isinstance(x, str) for x in aliases) or \
                    not isinstance(arg_required, bool) or not isinstance(many_args, bool):
                globalLog.warn(f"Option {opt_name} config is not set properly")
                continue

            comm_opt = CommandOpt(name=opt_name, arg_required=arg_required, many_args=many_args)
            for alias in aliases:
                res[alias] = comm_opt

        return res

    @staticmethod
    def _load_opts_postprocess(opts_post: Optional[Dict[str, Dict]]) -> Optional[
        List[Tuple[CommandTemplateParts, Dict]]]:
        if opts_post is None or not isinstance(opts_post, dict):
            globalLog.warn(f"Command config '{JsonCommandConfigLoader.OPTS_POSTPROCESS}' is not set properly")
            return None

        res = []
        for opts, task in opts_post.items():
            if not isinstance(opts, str):
                globalLog.warn(f"Wrong type of opts template in '{JsonCommandConfigLoader.OPTS_POSTPROCESS}'")
                continue
            if not isinstance(task, dict):
                globalLog.warn(f"Wrong type of task template in '{JsonCommandConfigLoader.OPTS_POSTPROCESS}'")
                continue

            opts_templ = TemplateConstructor().from_str(opts)
            if opts_templ is None:
                continue
            task_templ = JsonCommandConfigLoader._create_task_template(task)
            if task_templ is None:
                continue

            res.append((opts_templ, task_templ))

        return res

    @staticmethod
    def _load_config_from_json(path: str) -> Optional[List[CommandConfig]]:
        try:
            with open(path, "r") as inF:
                config = json.load(inF)
                res = []
                for name, comm_conf in config.items():
                    entry, examples, opts, opts_post = JsonCommandConfigLoader._load_entry(
                        comm_conf.get(JsonCommandConfigLoader.ENTRY, None)
                    ), JsonCommandConfigLoader._load_examples(
                        comm_conf.get(JsonCommandConfigLoader.EXAMPLES, None)
                    ), JsonCommandConfigLoader._load_opts(
                        comm_conf.get(JsonCommandConfigLoader.OPTS, None)
                    ), JsonCommandConfigLoader._load_opts_postprocess(
                        comm_conf.get(JsonCommandConfigLoader.OPTS_POSTPROCESS, None)
                    )

                    if entry is None or examples is None or opts is None or opts_post is None:
                        globalLog.warn("Could not create command config")
                        continue
                    res.append(CommandConfig(
                        entry=entry, examples=examples,
                        opts=opts, opts_postprocess=opts_post
                    ))
            return res

        except OSError:
            globalLog.warn(f"Failed to read config from file - {path}")
            return None


init_command_config_loader = JsonCommandConfigLoader()
