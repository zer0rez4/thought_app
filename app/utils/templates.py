from jinja2 import Template
from pathlib import Path


def render_email_template(
        template_path: str, 
        **kwargs
) -> Template:

    template = Path(template_path).read_text(
        encoding='UTF-8'
    )

    return Template(template).render(**kwargs)
