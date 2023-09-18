import dataclasses

from src.ansible_matcher.template_lang.main import CommandWords, TemplateWords
from src.ansible_matcher.extracted_matching.opts_extraction import CommandOpts, TemplateOpts


@dataclasses.dataclass
class ExtCommand:
    params: CommandWords = dataclasses.field(default_factory=list)
    opts: CommandOpts = dataclasses.field(default_factory=dict)
    redirects: CommandWords = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ExtTemplate:
    params: TemplateWords = dataclasses.field(default_factory=list)
    opts: TemplateOpts = dataclasses.field(default_factory=dict)
    redirects: TemplateWords = dataclasses.field(default_factory=list)
