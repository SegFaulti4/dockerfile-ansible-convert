from typing import Dict, Set, List, Any, Tuple

from src.shell.main import ShellWordObject
from src.ansible_matcher.command_extraction import Opt, CommandCallOpts


def pip_extra_args(unmatched_opts: CommandCallOpts, opts_name_mapping: Dict[str, Opt],
                   opts_alias_mapping: Dict[str, Opt], extra_args: List[str], module_params: Dict[str, Any]) \
        -> Tuple[Dict[str, Any], CommandCallOpts]:

    opts_copy: Dict[str, List[ShellWordObject]] = {k: v for k, v in unmatched_opts.items()}
    extra_args_opts = {opts_alias_mapping[x] for x in extra_args}
    extra_args = ""

    for opt_name, opt_args in opts_copy.items():
        opt = opts_name_mapping[opt_name]
        # generally the last one should be one of the longest
        opt_alias = opt.aliases[-1]
        if opt in extra_args_opts:
            if not opt_args:
                extra_args += opt_alias + " "
            else:
                extra_args += "".join(opt_alias + " " + arg.value + " " for arg in opt_args)
            del unmatched_opts[opt_name]

    pip_module = "ansible.builtin.pip"
    if pip_module not in module_params:
        module_params[pip_module] = dict()
    module_params[pip_module]["extra_args"] = extra_args
    return module_params, unmatched_opts
