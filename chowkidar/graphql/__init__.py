import os

from ariadne import load_schema_from_path

from .view import *
from .decorators import *
from .processors import auth_mutations as am

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

auth_type_defs = load_schema_from_path(BASE_DIR + '/graphql/schema/')

auth_processors = [
    am
]

__all__ = [
    'GraphQLView',
    'AuthenticatedChannel',
    'auth_type_defs',
    'auth_processors',
    'login_required',
]
