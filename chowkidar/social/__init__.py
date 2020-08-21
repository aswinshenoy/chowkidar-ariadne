import os

from ariadne import load_schema_from_path

from .processors import social_auth_mutations

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

social_auth_type_defs = load_schema_from_path(BASE_DIR + '/social/schema/')

social_auth_processors = [
    social_auth_mutations
]

__all__ = [
    'social_auth_type_defs',
    'social_auth_processors',
]
