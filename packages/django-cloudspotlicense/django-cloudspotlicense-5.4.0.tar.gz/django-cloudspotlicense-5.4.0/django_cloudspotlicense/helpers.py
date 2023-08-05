from .models import GlobalPermission

def revoke_permissions(user):
    """ Removes all the permissions for the specified user """
    
    user.user_permissions.clear()
    
    # Trigger the DB to avoid caching issues
    user.save() 
    
def grant_permissions(user, permissions):
    """ Grants a list of permissions to the specified user. If a permission does not exist, it gets created first. """
    
    for permission in permissions:
        
        # We check if the permission exists in the app already, if so, we assign it to the user
        # Otherwise, we first have to create the permission and then assign it
        db_permission = GlobalPermission.objects.filter(codename=permission).first()
        if not db_permission: db_permission = GlobalPermission.objects.create(codename=permission, name=permission)
        
        user.user_permissions.add(db_permission)