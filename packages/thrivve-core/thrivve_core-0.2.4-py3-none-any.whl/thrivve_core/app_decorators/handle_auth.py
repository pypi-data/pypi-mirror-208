from functools import wraps

from flask import request

from thrivve_core.helpers.auth import verify_user_token_v2
from thrivve_core.helpers.exceptions import (
    AppValidationError,
    AppMissingAuthError,
)
# from thrivve_core.helpers.acl_enum import Permission


def handle_auth(require_auth, append_auth_args=None, allowed_roles=None, pre_login=False, allowed_permissions=None):
    def factory(func):
        @wraps(func)
        def inner_function(*args, **kws):
            if not require_auth:
                return func(*args, **kws)

            if "Authorization" not in request.headers:
                raise AppMissingAuthError("Missing authentication")

            token = request.headers["Authorization"]
            if "country_code" not in request.headers and request.endpoint != "health_check":
                raise AppValidationError("Country Code is Required (c)")

            user = verify_user_token_v2(token=token)

            if not pre_login:
                if not user.get("is_logged"):
                    raise AppValidationError("Not Logged Token, please complete login process")

            if allowed_roles:
                if user.get("role") not in allowed_roles:
                    raise AppValidationError("Not Allowed Role")

            if append_auth_args and isinstance(append_auth_args, list):
                for arg in append_auth_args:
                    if not kws.get('appended_kws'):
                        kws['appended_kws'] = dict()
                    if '.' in arg:

                        if 'as' in arg:
                            arg, as_arg = arg.split(' as ')
                        else:
                            as_arg = arg.replace('.', '_')

                        obj, key = arg.split('.')
                        value = user.get(obj, {}).get(key)

                        kws['appended_kws'][as_arg] = value
                    else:
                        value = user.get(arg)
                        kws['appended_kws'][arg] = value

            return func(*args, **kws)

        return inner_function

    return factory
