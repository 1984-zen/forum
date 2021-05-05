from django import template

register = template.Library()

@register.filter
def add_multiply(value, arg):
    #value: 流水號(forloop.counter)
    #arg: 目前頁數(從url網址的queryString取得page=)
    #公式: 流水號 + (目前頁數 - 1) * 20
    result = value + (int(arg) - 1) * 20
    return result
