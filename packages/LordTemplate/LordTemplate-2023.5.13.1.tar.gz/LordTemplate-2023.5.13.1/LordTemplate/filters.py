import subprocess
import textwrap

from LordPath.opener.json import load_json
import regex as re
import json
import yaml
import shlex

from dateutil.parser import parse as dateparse
import LordUtils
from LordUtils import sorting
from LordUtils.json_encoder import JEncoder

from .jinja_env import jenv, regist_filter, regist_global, regist_test
from . import table as table_gen
from pyfiglet import figlet_format
import art

from jinja2 import pass_context
from jinja2.runtime import Context


# Value Filters


@pass_context
@regist_filter('set')
def set_var_filter(ctx: Context, value, var_name):
    ctx.vars[var_name] = value
    ctx.exported_vars.add(var_name)
    # setattr(ctx, var_name, value)
    return ''

@pass_context
@regist_global('get')
def get_var_filter(ctx: Context, var_name):
    value = {**ctx.vars, **ctx.parent}.get(var_name)
    return value


@pass_context
@regist_global('load_table')
def load_table(context: Context, table_path):
    # todo load table_list from dataset with table_name
    table_list = load_json(table_path)
    for row in table_list['table']:
        for col in row:
            t = context.environment.from_string(col['text'])
            rendered_value = t.render(**context.parent, **context.vars)
            col['text'] = rendered_value
    r = table_gen.format_table(table_list)
    return r


@regist_global('length')
def length_var(value):
    return len(value)


@regist_filter('linebreak')
def linebreak(value, s):
    """replace linebreak with symbol"""
    if isinstance(value, str):
        value = f"{s}\n".join(value.splitlines())
    return value


@regist_filter('date')
def date_format(value, strtime):
    """reformate Date string"""
    dt = dateparse(value)
    return dt.strftime(strtime)


@regist_filter('to_json')
def to_json(value):
    return JEncoder.to_json_string(value)


@regist_filter('to_yaml')
def to_yaml(value):
    return yaml.dump(value)


@regist_filter('to_data')
def to_data(value):
    o = json.loads(value)
    return o


# text align

@regist_filter('center_text')
def center_text(value: str, width, fill_up=' '):
    width = int(width)
    r = str(value).center(width, fill_up)
    return r


@regist_filter('align_right')
def align_right(value: str, width, fill_up=' '):
    width = int(width)
    r = str(value).rjust(width, fill_up)
    return r


@regist_filter('align_left')
def align_left(value: str, width, fill_up=' '):
    width = int(width)
    r = str(value).ljust(width, fill_up)
    return r

# end align


@pass_context
@regist_filter('render')
@regist_global('render')
def render(context: Context, value, **kwargs):
    t = context.environment.from_string(value)
    value = t.render(**context.parent, **context.vars, **kwargs)
    return value


@regist_filter('text2art')
def ascii_art(value, font=art.DEFAULT_FONT):
    return art.text2art(value, font=font)


question_cache = {

}


@pass_context
@regist_global('question')
def question(context: Context, value, id=None):
    t = context.environment.from_string(value)
    question_text = t.render(**context.parent, **context.vars)

    if id in question_cache:
        return question_cache[id]

    v = input(question_text + '  ')

    if id is not None:
        question_cache[id] = v

    return v


def __num_sort_preformat(v):
    if hasattr(v, 'get_sorting_key'):
        f = v.get_sorting_key
        if callable(f):
            return f()

    return str(v)


@regist_filter('num_sort')
def num_sort(value):
    """sort list numeric"""
    return sorting.sort_numeric(value, preformat=lambda x: __num_sort_preformat(x))


data_lang = None


# Test Functions

fn_match_value = LordUtils.fn_match_value

# FILTERS

# build in filters: https://jinja.palletsprojects.com/en/3.1.x/templates/#builtin-filters

jenv.filters['figlet'] = figlet_format  # http://www.figlet.org/examples.html
# lambda - filters
jenv.filters['regex'] = lambda value, reg, repl: re.sub(reg, repl, value)  # regex replace with sub
# TESTS - Functions  -> https://jinja.palletsprojects.com/en/3.1.x/api/#custom-tests
jenv.tests['fnmatch'] = fn_match_value
