# Chowkidar
### JWT Authentication for Django Ariadne

An JWT-based authentication package for django, with Ariadne GraphQL integration support.

### Features
* Token & Refresh Token based JWT Authentication
* Tokens stored as server-side cookie
* Ability to Auto-Refresh JWT Token if Refresh Token Exists
* Out-of-the-box support for Ariadne GraphQL integration
* Get current logged-in user in info.context of resolvers


### How to Integrate?
Currently, we have not packaged this application, and hence to install this, you are supposed
to add the `chowkidar` package (i.e. directory) inside your root Django project.

Add `chowkidar` to `INSTALLED_APPS` and run migrations to apply required db changes to the database.

#### Integration with Ariadne
In `urls.py`, replace the GraphQLView coming from the Ariadne with the one from this package
```python3
# from ariadne.contrib.django.views import GraphQLView
from chowkidar.graphql import GraphQLView
```
```python3
urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(schema=schema), name='graphql'),
    ...
]
```

Also to your schema, add `auth_type_defs` and `auth_processors` from this package
```python3
from chowkidar.graphql import auth_type_defs, auth_processors
```

```python3
types = [
    ...
    auth_type_defs,
    ...
]

processors = [
    ...
    *auth_processors,
    ...
]

schema = make_executable_schema(types, *processors)
```

### Credits
This project is heavily inspired by django-graphql-jwt by flavors, and is loosely forked
from its implementation. 

### License
This project is licensed under MIT