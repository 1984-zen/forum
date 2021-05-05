from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    check_value = value.split("_")[0]
    if len(check_value) == 12:
        return f'/{value.replace("_", " ").split(" ", 1)[0]}'
    else:
        return ""