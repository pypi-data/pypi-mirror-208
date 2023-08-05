# Cloudspot API wrapper
Basic wrapper for the Cloudspot License API.

# Use cases
1. Authenticate and authorize users on an external app, linked to Cloudspot License

# Getting started

### Install

Install with pip.

```python
pip install cloudspot-license-api
```

### Import

```python
from cloudspotlicense.api import CloudspotLicense_API
```

# Functionalities

### Setup

When setting up the class, one parameter is expected: the id of the external application as present on the license server.
This is a crucial and important step. This id is used to determine what application is making the request and what permissions are linked to it.
By using a wrong id, your users will be able to authenticate themselves if their credentials are correct but the permissions will not be mapped correctly. This may lead to giving users too much or too little permissions on the external application.

```python
from cloudspotlicense.api import CloudspotLicense_API
api = CloudspotLicense_API('app-id')
```

### Authentication and authorization

After setting up the connection, you can use the ```api``` to send requests to the Cloudspot License.
Users that are trying to log in will give their username and password. Send this username and password to the License server to validate their credentials.
If correct, the License server will return a token and the user's permissions for the external application. If not correct, a ```BadCredentials``` error will be raised.

```python
try:
    api.authenticate(username, password)
except BadCredentials as e:
    print(e)
```

If a request is succesful, you can retrieve the returned token and permissions by using ```api.token``` and ```api.permissions``` respectively.

The ```api.permissions``` will contain an ```AuthPermissions``` object. This is a list of ```AuthPermission``` objects.
An ```AuthPermission``` object looks like this:

```yaml
[
  {
        "company_id": "COMPANY_ID_1",
        "company_name": "COMPANY_NAME_1",
        "permissions": [
            "use_app"
        ]
    },
    {
        "company_id": "COMPANY_ID_2",
        "company_name": "COMPANY_NAME_2",
        "permissions": [
            "use_xxx",
            "get_xxx",
            "use_app"
        ]
    }
]
```

It contains the permissions for each company the user is part of. The ```use_app``` permission is crucial and is always present. If this permission is not present, a user will not be able to authenticate for this company on the external application. A company that hasn't got the ```use_app``` permission assigned, will not be included in the response.

You can loop over the permissions as follows:

```python
for company_perm in api.permissions.items():
    print(company_perm.company_id) # Prints the id of the company
    print(company_perm.company_name) # Prints the name of the company
    print(company_perm.permissions) # Prints an array of all the permissions (slugs)

    for perm in company_perm.permissions:
        print('perm: ', perm) # Prints the slug of the permission
```

### Retrieving permissions for a specific company, external application and user

You can retrieve the permissions for an external application for a specific user and company. You can only use this function after succesfully authenticating or supplying a token.

```python
from cloudspotlicense.api import CloudspotLicense_API

# 1: authenticate first
api = CloudspotLicense_API('app-id')
auth = api.authenticate('email@example.com', 'my-pwd')

permissions = api.get_company_permissions('company-id')
print('permissions: ', permissions) # Prints an array of all the permissions (slugs)

# 2: OR supply a token
api = CloudspotLicense_API('app-id')
permissions = api.get_company_permissions('company-id', token='token')
print('permissions: ', permissions) # Prints an array of all the permissions (slugs)
```

### Retrieving user info

By default, an empty ```User``` object will be attached to the ```api```. You can retrieve the object with ```api.user```.
To populate the ```User```, you need to execute the function ```api.get_user()``` first.

The ```User``` object has four attributes: ```first_name```, ```last_name```, ```email``` and ```company```.

If you've already authenticated the user before using the ```api```, you do not need to supply a token to the function.
If you're using a new ```api``` object and want to retrieve the user for a specific token without authenticating first, you can supply the token to the function.

If succesful, the user will be attached to ```api.user``` and overwrite any previous user.

Retrieve user by authenticating first.

```python

api.authenticate(username, password)
api.get_user()
    
print(user.first_name)
```

Retrieve user by supplying a token. You can catch the error ```NoValidToken``` to handle a token that is not valid.

```python

try:
    api.get_user(token)
except NoValidToken as e:
    print(e)
    
print(user.first_name)
```