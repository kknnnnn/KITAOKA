from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """辞書から指定したキーに対応する値を返す"""
    return dictionary.get(key)
