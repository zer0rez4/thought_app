from jinja2 import Template
from pathlib import Path


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'templates'


def render_email_template(
    template_name: str,
    **kwargs
) -> str:
    template_path = TEMPLATES_DIR / template_name

    template = template_path.read_text(
        encoding='utf-8'
    )

    return Template(template).render(**kwargs)
