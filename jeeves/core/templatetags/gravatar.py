from django import template
import hashlib

register = template.Library()


@register.filter(name='gravatar')
def gravatar(email):
    return "https://gravatar.com/avatar/{}" \
        .format(hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest())
