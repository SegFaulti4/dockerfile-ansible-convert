from typing import Optional, Tuple

from src.ansible_matcher.template_lang.main import \
    CommandWords, TemplateWords, \
    TemplateMatcher, TemplateTweaks, TemplateMatchResult
from src.ansible_matcher.extracted_matching.opts_extraction import CommandOpts, TemplateOpts
from src.ansible_matcher.extracted_matching.command_extraction import ExtCommand, ExtTemplate

from src.ansible_matcher.utils import listify


def match_ext_call(extracted_call: ExtCommand,
                   extracted_tmpl: ExtTemplate, template_tweaks: TemplateTweaks) \
        -> Tuple[Optional[TemplateMatchResult],
                 Optional[CommandOpts]]:
    params_fields = match_ext_call_params(
        extracted_call.params, extracted_tmpl.params, template_tweaks=template_tweaks)
    if params_fields is None:
        return None, None

    redirects_fields = match_ext_call_redirects(
        extracted_call.redirects, extracted_tmpl.redirects, template_tweaks=template_tweaks)
    if redirects_fields is None:
        return None, None

    opt_fields, unmatched_opts = match_extracted_call_opts(
        extracted_call.opts, extracted_tmpl.opts, template_tweaks=template_tweaks)
    if opt_fields is None:
        return None, None

    match_res = TemplateMatcher.merge_match_results(params_fields, opt_fields)
    if match_res is None:
        return None, None

    return match_res, unmatched_opts


def match_ext_call_params(call_params: CommandWords,
                          tmpl_params: TemplateWords, template_tweaks: TemplateTweaks) \
        -> Optional[TemplateMatchResult]:
    params_matcher = TemplateMatcher(tmpl=tmpl_params, tweaks=template_tweaks)
    return params_matcher.full_match(call_params)


def match_ext_call_redirects(call_redirects: CommandWords,
                             tmpl_redirects: TemplateWords, template_tweaks: TemplateTweaks) \
        -> Optional[TemplateMatchResult]:
    redirects_matcher = TemplateMatcher(tmpl=tmpl_redirects, tweaks=template_tweaks)
    return redirects_matcher.full_match(call_redirects)


def match_extracted_call_opts(call_opts: CommandOpts,
                              tmpl_opts: TemplateOpts, template_tweaks: TemplateTweaks) \
        -> Tuple[Optional[TemplateMatchResult],
                 Optional[CommandOpts]]:
    opt_fields = dict()
    unmatched_opts = {k: listify(v) for k, v in call_opts.items()}

    for k, v in tmpl_opts.items():
        if k not in call_opts:
            return None, None
        v = listify(v)

        if not v and not unmatched_opts[k]:
            del unmatched_opts[k]
            continue
        if not v or not unmatched_opts[k]:
            return None, None

        opt_matcher = TemplateMatcher(tmpl=v, tweaks=template_tweaks)
        tmp_fields, unmatched = opt_matcher.match(call_opts[k])
        if tmp_fields is None:
            return None, None

        opt_fields = TemplateMatcher.merge_match_results(opt_fields, tmp_fields)
        if opt_fields is None:
            return None, None

        if not unmatched:
            del unmatched_opts[k]
        else:
            unmatched_opts[k] = unmatched

    return opt_fields, unmatched_opts
