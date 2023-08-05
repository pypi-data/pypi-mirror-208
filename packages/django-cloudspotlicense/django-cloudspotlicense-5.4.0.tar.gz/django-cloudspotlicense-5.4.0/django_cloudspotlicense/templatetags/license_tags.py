from django import template
from django_cloudspotlicense import PACKAGE_NAME
from django_cloudspotlicense.utils import has_perm as util_has_perm

register = template.Library()

@register.filter(name='has_perm')
def has_perm(user, perm):
    """ Returns True if user has the specified permission on the Cloudspot License server. """
    return util_has_perm(user, perm)