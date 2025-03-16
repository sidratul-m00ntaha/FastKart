from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key), 0)
    return 0
