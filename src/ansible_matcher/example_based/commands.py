import dataclasses
from typing import Union, Optional, Dict, Any

from src.shell.main import *
from src.ansible_matcher.example_based.template_lang import \
    TemplateField, TemplatePart, CommandCallParts, CommandTemplateParts
from src.ansible_matcher.example_based.opts_extraction import CommandOpt


class CommandConfig:
    entry: Any
    examples: List[Tuple[CommandTemplateParts, Dict[str, Any]]]
    opts: Dict[str, CommandOpt]
    opts_postprocess: List[Tuple[CommandTemplateParts, Dict[str, Any]]]


class _CommandConfigLoader:

    def load(self, comm: CommandCallParts) -> CommandConfig:
        raise NotImplementedError


command_config_loader = _CommandConfigLoader()
