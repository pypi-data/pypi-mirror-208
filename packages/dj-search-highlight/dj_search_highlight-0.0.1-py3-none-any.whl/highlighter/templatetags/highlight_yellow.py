from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def highlight_yellow(text, value):
    if text is not None:
        text = str(text)
        src_str = re.compile(value, re.IGNORECASE)
        str_replaced = src_str.sub(f"<span style=\"background-color:red;\">{value}</span>", text)
    else:
        str_replaced = ''

    return mark_safe(str_replaced)