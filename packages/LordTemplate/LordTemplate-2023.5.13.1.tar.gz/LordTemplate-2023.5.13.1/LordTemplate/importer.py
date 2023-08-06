import sys
import os
import inspect
from pathlib import Path

from LordUtils.decorators import CachedProperty
from jinja2 import FileSystemLoader

from .jinja_env import jenv, regist_loader

from importlib.abc import MetaPathFinder, Loader
from importlib.util import spec_from_loader
from typing import Any, Optional, Tuple, Type, Union

# Experimental
CUSTOM_EXTENSIONs = ['.jinja2', '.j2']


class JinjaModule:
    def __init__(self, module_name: str, filepath: Path) -> None:
        self.filepath = Path(filepath)
        self.module_name = module_name
        self.module_path: Optional[Path] = None

        for parent in self.filepath.parents:
            if parent.name == module_name:
                self.module_path = parent
                break

    @CachedProperty
    def template_path(self) -> str:
        sub_path = self.filepath.relative_to(self.module_path)

        return f"{self.module_name}/{str(sub_path)}"

    def init(self) -> None:
        regist_loader(self.module_name, FileSystemLoader(self.module_path))
        self.template = jenv.get_template(self.template_path)

    def render_str(self, s: str, **kwargs: Any) -> str:
        t = jenv.from_string(s)
        return t.render(
            __class__=self,
            __place__=kwargs,
            **kwargs
        )

    def render_template(self, **kwargs: Any) -> str:
        output = self.template.render(
            __class__=self,
            __place__=kwargs,
            **kwargs
        )
        return output

    def render(self, **kwargs: Any) -> str:
        return self.render_template(**kwargs)


class JinjaTemplateLoader(Loader):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        self.jinja_module: Optional[JinjaModule] = None

    def create_module(self, spec: Any) -> None:
        module_name = spec.parent.split('.')[0]
        self.jinja_module = JinjaModule(module_name, self.filepath)

    def exec_module(self, module: Any) -> None:
        # here we update module and add our custom members
        self.jinja_module.init()
        # Aktualisieren des Moduls mit den Funktionen und Variablen von JinjaModule
        module.jinja_module = self.jinja_module
        function_names = [name for name, _ in inspect.getmembers(self.jinja_module.__class__, inspect.isfunction)]
        for func_name in function_names:
            f = getattr(self.jinja_module, func_name)
            # setattr(module, func_name, Caller(f))
            setattr(module, func_name, f)


class JinjaPathFinder(MetaPathFinder):
    def find_spec(self, fullname: str, path: Optional[Union[str, Tuple[str, ...]]], target: Optional[Any] = None) -> Optional[Any]:
        mod_name = fullname.split(".")[-1]

        paths = path if path else [os.path.abspath(os.curdir)]

        for check_path in paths:
            for extension in CUSTOM_EXTENSIONs:
                filepath = os.path.join(check_path, mod_name + extension)

                if os.path.exists(filepath):
                    return spec_from_loader(fullname, JinjaTemplateLoader(filepath))

        return None


def init_finder():
    sys.meta_path.insert(0, JinjaPathFinder())
