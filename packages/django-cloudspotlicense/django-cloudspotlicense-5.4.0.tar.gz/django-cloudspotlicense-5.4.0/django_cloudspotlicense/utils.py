from django_cloudspotlicense import PACKAGE_NAME

def has_perm(user, perm):
    """ Returns True if user has the specified permission on the Cloudspot License server. """
    license_perm = '{0}.{1}'.format(PACKAGE_NAME, perm)
    return user.has_perm(license_perm)