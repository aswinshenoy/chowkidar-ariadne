from ..utils import exceptions


def login_required(resolver):
    """Requires login for a resolver"""

    def wrapper(parent, info, *args, **kwargs):
        user = getattr(info.context, "user", None)
        if user is not None and not user.is_anonymous:
            resolved = resolver(parent, info, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied(message='User not authenticated', code='AUTHENTICATION_REQUIRED')
        return resolved

    return wrapper


__all__ = [
    'login_required',
]
