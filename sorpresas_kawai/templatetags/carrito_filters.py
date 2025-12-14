from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """
    Permite acceder a un valor de diccionario usando una clave dinámica
    dentro de las plantillas de Django.
    Uso: {{ diccionario|get:clave }}
    """
    return dictionary.get(key)