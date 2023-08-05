from jinja2 import (
    Environment,
    PackageLoader,
    Template,
    TemplateError,
    TemplateNotFound,
    TemplateRuntimeError,
    select_autoescape,
)

from lupin_grognard.core.tools.utils import die, info, write_file


class JinjaGenerator:
    def __init__(self, *args):
        super().__init__(*args)

    def _get_local_template(self, template_name: str) -> Template:
        try:
            env = Environment(
                loader=PackageLoader("lupin_grognard", "templates"),
                autoescape=select_autoescape(),
                trim_blocks=True,  # Removes unnecessary spaces before and after blocks and loop
                lstrip_blocks=True,  # Removes unnecessary spaces before blocks and loop
            )
            return env.get_template(template_name)
        except TemplateNotFound:
            die(msg=f"Template 'lupin_grognard/templates/{template_name}' not found")

    def _generate_file(
        self, path: str, file_name: str, file_extension: str, context={}
    ) -> None:
        template = self._get_local_template(template_name=f"{file_name}.j2")
        try:
            content = template.render(context)
        except (TemplateError, TemplateRuntimeError) as e:
            die(msg=f"Error rendering Jinja2 template: {e}")
        if not path:
            info(msg=f"Generating {file_name}{file_extension} file")
            write_file(file=f"{file_name}{file_extension}", content=content)
        else:
            info(msg=f"Generating {path}/{file_name}{file_extension} file")
            write_file(file=f"{path}/{file_name}{file_extension}", content=content)
        info(msg="File generated")
