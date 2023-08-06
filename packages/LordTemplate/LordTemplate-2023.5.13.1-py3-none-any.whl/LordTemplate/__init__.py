from . import jinja_env
from . import filters

jenv = jinja_env.jenv


def jenv_render_str(s: str, placeholder: dict):
    t = jenv.from_string(s)
    return t.render(**placeholder)


def reset_path_to(path="./"):
    jinja_env.reset_path(path)


class TemplateClass:

    def __init__(self, template, jenv=None):
        self.template = template
        self.placeholder = None

    @classmethod
    def get_template_by_path(cls, path):
        file = path.replace('\\', '/')
        template = jenv.get_template(file)
        return cls(template)

    @classmethod
    def get_template_from_text(cls, text):
        template = jenv.from_string(text)
        return cls(template)

    def set_placeholder(self, placeholders: dict = None):
        self.placeholder = placeholders

    def render_str(self, s):
        t = jenv.from_string(s)
        return t.render(
            **self.placeholder,
            __place__=self.placeholder,
            render=self.render_str
        )

    def render_template(self, **kwargs):
        output = self.template.render(
            self.placeholder,
            __class__=self,
            __place__=self.placeholder,
            render=self.render_str,
            **kwargs
        )
        return output
