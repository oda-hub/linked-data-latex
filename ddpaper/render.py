from __future__ import print_function
import importlib
import tempfile
import traceback
from jinja2.exceptions import TemplateRuntimeError
from jinja2.ext import Extension
from jinja2 import nodes
from ddpaper.filters import setup_custom_filters


import os
import re
import jinja2

from .yaml import yaml

import numpy as np
from jinja2.utils import concat

import logging

logger = logging.getLogger('ddpaper.render')


# FROM: https://github.com/duelafn/python-jinja2-apci/blob/master/jinja2_apci/error.py


class AttrDict(dict):
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise KeyError('key {} is not available, have keys: {}'.format(
                k, ", ".join(self.keys())))


class CallDict(dict):
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise KeyError('key {} is not available, have keys: {}'.format(
                k, ", ".join(self.keys())))



class RaiseExtension(Extension):
    # This is our keyword(s):
    tags = set(['raise'])

    # See also: jinja2.parser.parse_include()
    def parse(self, parser):
        # the first token is the token that started the tag. In our case we
        # only listen to "raise" so this will be a name token with
        # "raise" as value. We get the line number so that we can give
        # that line number to the nodes we insert.
        lineno = next(parser.stream).lineno

        # Extract the message from the template
        message_node = parser.parse_expression()

        return nodes.CallBlock(
            self.call_method('_raise', [message_node], lineno=lineno),
            [], [], [], lineno=lineno
        )

    def _raise(self, msg, caller):
        raise TemplateRuntimeError(msg)


def get_latex_jinja_env():
    env = jinja2.Environment(
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix=r'%%\LINE',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath('.')),
        undefined=jinja2.StrictUndefined,
        extensions=[RaiseExtension],
    )
    setup_custom_filters(env)
    return env


def extract_referenced_keys(template_string):
    reduced = []
    for k in re.findall(r"\\VAR{(.*?)}", template_string):
        if not k in reduced:
            logger.info("found key %s", k)
            reduced.append(k)
    return reduced


def extract_template_data(template_string):
    keys = extract_referenced_keys(template_string)

    re_eq = re.compile("(.*?)==(.*)")

    template_data = []

    for key in keys:
        r = re_eq.match(key)
        if r:
            k, v = r.groups()
        else:
            k = key
            v = None

        template_data.append((key, k, v))

    return template_data


def load_modules_in_env(latex_jinja_env, key):
    if key.strip().startswith('local.'):
        local_marker, module_name, remainder = key.split(".", 2)

        module = importlib.import_module(module_name)

        logger.info('imported %s as %s', module_name, module)

        latex_jinja_env.globals['local'] = AttrDict(**{module_name: module})

        return key  # module_name+"."+remainder

    if key.strip().startswith('oda.'):
        logger.info("loading oda plugin")

        import odafunction

        logger.info('imported odafunction as %s', odafunction)

        latex_jinja_env.globals['oda'] = AttrDict(
            **{'evaluate': module.evaluate})

    # if key.strip().startswith('oda.'):
    #     logger.info("loading oda plugin")

    #     module = importlib.import_module("oda")

    #     logger.info('imported odahub as %s', module)

    #     latex_jinja_env.globals['oda'] = AttrDict(
    #         **{'evaluate': module.evaluate})

    return key


def compute_value(latex_jinja_env, key, data, allow_incomplete=True):
    newkey = load_modules_in_env(latex_jinja_env, key)

    logger.info('compute value for key %s', newkey)

    try:
        rtemplate = latex_jinja_env.from_string("\VAR{"+newkey+"}")
    except:
        logger.exception('unable to parse template %s', newkey)
        raise


    try:
        d_value = rtemplate.render(data)  # .encode('utf8')
    except Exception as e:
        print("unable to render", key, e)
        traceback.print_exc()

        d_value = "XXX"
        # if not allow_incomplete:
        #    raise

    return d_value


def render_definitions(latex_jinja_env, template_string, data):
    header = """
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% generated by template.py, please do not edit directly
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% boilerplate

\def\\addVAR#1#2{\expandafter\gdef\csname my@data@\detokenize{#1}\endcsname{#2}}
\def\VAR#1{%
  \ifcsname my@data@\detokenize{#1}\endcsname
    \csname my@data@\detokenize{#1}\expandafter\endcsname
  \else
    \expandafter\ERROR
  \\fi
}
\def\DATA#1{%
  \ifcsname my@data@\detokenize{#1}\endcsname
    \csname my@data@\detokenize{#1}\expandafter\endcsname
  \else
    \expandafter\ERROR
  \\fi
}

\def\ASSUME#1{%
}

\def\LOAD#1{%
}

\def\GET#1{%
}
% extracted definitions

"""

    template_string, preprocs = preproc_template(template_string)
    template_string, loaded_data = extract_loads_template(
        latex_jinja_env, template_string)

    data = {**data, **loaded_data}

    preprocs_dict = dict(preprocs)

    logger.info("preprocs dict %s", preprocs_dict)

    template_data = extract_template_data(template_string)

    output = header
    for l_key, key, value in template_data:
        d_value = compute_value(latex_jinja_env, key, data)

        logger.debug("key: %s, value: %s; long key: %s; data value %s" %
                     (key, value, l_key, d_value))

        nref = 0
        for k, v in preprocs_dict.items():
            if l_key == v:
                logger.debug('found reference %s to %s', k, v)
                output += r"\addVAR{"+k+"}{"+d_value+"}\n"
                nref += 1

        if nref == 0:
            output += r"\addVAR{"+l_key+"}{"+d_value+"}\n"

    return output


def extract_loads_template(latex_jinja_env, template_string):
    logger.info("extracting load statements in %s", template_string)

    re_load_sources = re.compile(r"\\LOAD{(.*?)}", re.M)

    data = {}

    for source_fn in re_load_sources.findall(template_string):
        logger.info("loading from %s", source_fn)

        if source_fn.endswith(".yaml"):
            for k,v in yaml.load(open(source_fn)).items():

                try:
                    import oda 
                except Exception as e:
                    pass

                with tempfile.NamedTemporaryFile(suffix=".py") as f:
                    f.write(v.encode())
                    f.flush()
                    logger.info("storing module as %s", f.name)
                    spec = importlib.util.spec_from_file_location(k, f.name)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    data[k] = module


                logger.info("loading %s from %s as %s", k, v, data[k])
        elif source_fn.endswith(".py"):
            name = re.search("(.*?).py", os.path.basename(source_fn)).group(1)
            logger.info("loading from %s as %s", source_fn, name)

            spec = importlib.util.spec_from_file_location(name, source_fn)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            data[name] = module
            
            for k in getattr(module, '__all__', []):
                data[k] = getattr(module, k)
        else:
            raise NotImplementedError(f"can not load unknown kind of file {source_fn}")

    template_string = re_load_sources.sub("", template_string)

    return template_string, data


def preproc_template(template_string):
    logger.info("preprocessing template %s", template_string)

    re_preproc_sources = re.compile(r"\\ASSUME{(.*?)}", re.M)

    preprocs = []

    for preproc_source_fn in re_preproc_sources.findall(template_string):
        for re_in, re_out in yaml.load(open(preproc_source_fn)).items():
            logger.info('applying preproc %s => %s', re_in, re_out)

            for g in re.findall("("+re_in+")", template_string):
                f_re_in = g[0]
                logger.info("found preproc target %s", f_re_in)

                f_re_out = re.sub(re_in, re_out, f_re_in)

                preprocs.append((f_re_in, f_re_out))

            template_string = re.sub(re_in, re_out, template_string)

    template_string = re_preproc_sources.sub("", template_string)

    logger.info("preproc yeilds %s", template_string)

    return template_string, preprocs


def render_draft(latex_jinja_env, template_string, data, write_header=True):
    re_var = re.compile(r"\\VAR{(.*?)==(.*?)}")

    draft_vars = re_var.findall(template_string)
    for k, v in draft_vars:
        logger.info("draft var: %s %s", k, v)

    template_string, preprocs = preproc_template(template_string)

    template_string, loaded_data = extract_loads_template(
        latex_jinja_env, template_string)
    
    data = {**data, **loaded_data}

    ready_template = re_var.sub(r"\\VAR{\1}", template_string)

    re_all_var = re.compile(r"\\VAR{(.*?)}")
    draft_vars = re_all_var.findall(template_string)

    for k in draft_vars:
        load_modules_in_env(latex_jinja_env, k)
        logger.info("processed draft var: %s", k)

    logger.debug("processed template:\n %s", ready_template)

    template = latex_jinja_env.from_string(ready_template)

    if write_header:
        header = """
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% generated by template.py, please do not edit directly
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
    else:
        header = ""

    raw_render = concat(
        template.root_render_func(template.new_context(data, shared=False))
    )

    rendering = header+raw_render

    return rendering


def render_update(latex_jinja_env, template_string, data):
    template_data = extract_template_data(template_string)

    updated_template = template_string

    for l_key, key, value in template_data:
        d_value = compute_value(latex_jinja_env, key, data)

        logger.debug("key: %s, value: %s; long key: %s; data value %s" %
                     (key, value, l_key, d_value))

        updated_template = updated_template.replace(
            r"\VAR{%s==%s}" % (key, value),
            r"\VAR{%s == %s}" % (key.strip(), d_value.strip()),
        )

    return updated_template


def render_validate(latex_jinja_env, template_string, data):
    template_data = extract_template_data(template_string)

    for l_key, key, value in template_data:
        d_value = compute_value(latex_jinja_env, key, data)
        logger.info("key: %s value: \"%s\", new value: \"%s\"" %
                    (key, value, d_value))

        if value is not None and value != d_value:
            raise RuntimeError(
                "invalid! key: %s value %s: new value: %s" % (key, value, d_value))

    return ""
