from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    check_value = value.split("_")[0]
    if check_value[0] == "1" and check_value[1] == "6":
        return f'/{value.replace("_", " ").split(" ", 1)[0]}'
    else:
        return ""