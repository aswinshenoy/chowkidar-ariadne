# Chowkidar
### JWT Authentication for Django Ariadne

An JWT-based authentication package for django, with [Ariadne](https://github.com/mirumee/ariadne) GraphQL integration support.

### Features
* Token & Refresh Token based JWT Authentication
* Tokens stored as server-side cookie
* Ability to Auto-Refresh JWT Token if the Refresh Token Exists
* Support for Social Auth with `social-app-django`
* Support for Authenticated GraphQL Subscriptions with Django Channels
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

#### `login_required` decorator

```python3
from chowkidar.graphql import login_required

@some_resolver.field("myField")
@login_required
def resolve_field(self, info, sport=None, state=None, count=5, after=None):
    some_function()
```

### Social Auth
The type defs & processors for the Social Auth Mutations are available as follows -
```python3
from chowkidar.social import social_auth_type_defs, social_auth_processors
```

```graphql
mutation ($accessToken: String!){
  socialAuth(accessToken: $accessToken, provider: "google-oauth2")
  {
    success
    user
    {
      id
      username
      firstName
      lastName
      avatarURL
      isVIP
      isPremium
    }
  }
}
```

### GraphQL Subscriptions with Django Channels

In your `routing.py` -
```python3 
from django.urls import path

from channels.routing import URLRouter, ProtocolTypeRouter

from chowkidar.graphql import AuthenticatedChannel

from .graphql.schema import schema # replace this with your schema

application = ProtocolTypeRouter(
    {
        "websocket": (
            URLRouter(
                [path("ws/", AuthenticatedChannel(schema, debug=True))]
            )
        ),
    }
)
```

Doing this, you will get the logged-in user instance at `info.context['user']`,
which you can handle as per your wish. You can also use the `@login_required` decorator
that comes along with this package.

### Credits
This project is heavily inspired by `django-graphql-jwt` & `django-graphql-social-auth` by flavors, 
and is loosely forked from its implementation. 

### License
This project is licensed under the MIT License (MIT)