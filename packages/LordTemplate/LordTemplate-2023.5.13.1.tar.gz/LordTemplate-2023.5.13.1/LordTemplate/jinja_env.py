# Jinja
from jinja2 import Environment, FileSystemLoader, PrefixLoader, ChoiceLoader

# jinja2 setup code

file_loader = FileSystemLoader('./')


prefix_loaders = {}

loaders = [
    PrefixLoader(prefix_loaders),   # for the modules
    file_loader
]

j_loader = ChoiceLoader(loaders)

jenv = Environment(
    loader=j_loader
)

all_filters = {}
all_globals = {}
all_tests = {}


def get_base_loader():
    return jenv.loader.mapping['']


def reset_path(path="./"):
    file_loader.searchpath = [path]


def add_path(path):
    file_loader.searchpath.append(path)


def regist_loader(name, loader):
    prefix_loaders[name] = loader


def add_loader(loader, index=None):
    if index is None:
        loaders.append(loader)
    else:
        loaders.insert(0, loader)


def regist_filter(name):
    def inner(func):
        jenv.filters[name] = func
        all_filters[name] = func
        return func
    return inner


def regist_global(name):
    def inner(func):
        jenv.globals[name] = func
        all_globals[name] = func
        return func
    return inner


def regist_test(name):
    def inner(func):
        jenv.tests[name] = func
        all_tests[name] = func
        return func
    return inner