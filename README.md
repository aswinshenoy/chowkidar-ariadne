# Chowkidar
### JWT Authentication for Django Ariadne

An JWT-based authentication package for django, with [Ariadne](https://github.com/mirumee/ariadne) GraphQL integration support.

### Features
* Token & Refresh Token based JWT Authentication
* Tokens stored as server-side cookie
* Ability to Auto-Refresh JWT Token if the Refresh Token Exists
* Support for Social Auth with `social-app-django`
* Out-of-the-box support for [Ariadne](https://github.com/mirumee/ariadne) GraphQL integration
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

**Gotcha**

Your schema should already have the Mutation type, we only try to extend that type with the auth mutations.

### Mutations
```graphql
type Mutation {
  
  "Authenticates a user using email/username and password"
  authenticateUser(
    "Email address of the user"
    email: String
    "Username of the user"
    username: String
    "Password of the user"
    password: String!
  ): GenerateTokenResponse

  "Logs out the current user by revoking refresh token"
  logoutUser: Boolean
}
```

### Social Auth
The type defs & processors for the Social Auth Mutations are available as follows -
```python3
from chowkidar.social import social_auth_type_defs, social_auth_processors
```

### Credits
This project is heavily inspired by django-graphql-jwt by flavors, and is loosely forked
from its implementation. 

### License
This project is licensed under MIT