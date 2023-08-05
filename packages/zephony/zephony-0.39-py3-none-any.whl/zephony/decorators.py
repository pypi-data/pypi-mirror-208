import logging

from functools import wraps
from flask import request, redirect

from .exceptions import (
    ObjectNotFound,
    AccessForbidden,
    InvalidRequestData,
    UnauthorizedAccess,
    InvalidRequestSchema,
)
from .helpers import (
    validate_schema_with_errors,
)

from .models import BaseModel

logger = logging.getLogger(__name__)

def validate_schema(schema):
    """
    This function returns an empty list if there are no errors or a list of error
    dictionaries in case of an error(s).

    :param dict schema: The schema that the payload is to be validated against
    :param dict payload: The actual payload that has to be validated

    :return list(dict): Empty list if no errors
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload = request.get_json()

            errors = validate_schema_with_errors(schema, payload)
            if errors:
                raise InvalidRequestData(errors)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(token):
    """
    This decorator checks if the current user is permitted for the
    operation. Ideally, this decorator will be used in the resource layer while
    the `permission_required` decorator.

    :param str token: Permission required for token.

    :raises PermissionError:

    :return def:
    """

    def decorator(f):
        def decorated_function(*args, **kwargs):
            if request.user and request.user.is_admin:
                return f(*args, **kwargs)

            # If the user requesting is not owner, we check the permissions
            # operation here means object x action is an operation
            operation_permission = None
            for cls in BaseModel.__subclasses__():
                if cls.__name__ != 'Permission':
                    continue
                else:
                    operation_permission = cls.get_one(token)
                    break
                    
            if not operation_permission:
                # Control reaches here if the user is neither a owner,
                # nor does the requested permission exist on the database.

                # Psst! This shouldn't happen in an unbroken system. :(
                logger.error(
                    f'Permission token is invalid : {token}'
                )
                raise PermissionError('No permission token found')
            else:
                permission_bit = operation_permission.permission_bit
            
            # Check if the user can perform the requested action on the
            # resource(object). It also checks the permission of the parent
            # objects.
            if not int(request.role_permission_bit_sequence) & int(permission_bit):
                raise AccessForbidden(
                    message="You do not have valid permission to "
                    "perform this action on this resource."
                    " Please contact the administrator."
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator

