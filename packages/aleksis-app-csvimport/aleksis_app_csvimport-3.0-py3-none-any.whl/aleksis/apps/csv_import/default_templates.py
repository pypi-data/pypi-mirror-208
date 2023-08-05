import os

from ruamel.yaml import YAML

from .models import ImportTemplate


def update_or_create_templates_from_yaml(yaml_file: str):
    """Update or create import templates from a yaml file."""
    with open(yaml_file, "r") as f:
        yaml = YAML(typ="safe")
        template_defs = yaml.load(f)

    ImportTemplate.update_or_create_templates(template_defs, from_default=True)


def update_or_create_default_templates():
    """Update or create default import templates."""
    update_or_create_templates_from_yaml(
        os.path.join(os.path.dirname(__file__), "default_templates.yaml")
    )
