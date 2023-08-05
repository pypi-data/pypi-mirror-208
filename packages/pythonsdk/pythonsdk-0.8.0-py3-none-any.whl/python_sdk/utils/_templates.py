from string import Template


def render_template(template: str, template_values: dict[str, str], delimiter: str = "$") -> str:
    class CustomTemplate(Template):
        nonlocal delimiter
        delimiter = delimiter

    return CustomTemplate(template).substitute(**template_values)
