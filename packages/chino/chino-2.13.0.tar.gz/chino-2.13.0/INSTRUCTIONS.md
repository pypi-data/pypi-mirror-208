#  CHINO.io Python client <!-- omit in toc -->

*Official* Python wrapper for **CHINO.io** API,

Docs is available [here](http://docs.chino.io)

- - -
### Table of Content <!-- omit in toc -->
- [Usage instructions](#usage-instructions)
  - [API client](#api-client)
  - [SDK overview](#sdk-overview)
    - [Authentication](#authentication)
    - [User](#user)
    - [Group](#group)
    - [Permission](#permission)
    - [Repository](#repository)
    - [Schemas](#schemas)
    - [Document](#document)
    - [BLOB](#blob)
    - [SEARCH (**deprecated**)](#search-deprecated)
    - [UserSchemas](#userschemas)
    - [Collections](#collections)
    - [Consents (**deprecated**)](#consents-deprecated)
  - [Features](#features)
    - [Resource IDs](#resource-ids)
    - [Response structure and pagination](#response-structure-and-pagination)
    - [List iteration](#list-iteration)
    - [Search API](#search-api)
  - [SDK documentation](#sdk-documentation)
  - [Contributing to the SDK](#contributing-to-the-sdk)
      - [Build for pip](#build-for-pip)

- - -

## Install via pip

`pip install chino`

# Usage instructions

## API client
The `ChinoApiClient` class is the main client you will use to send API calls.

Create an instance of `ChinoApiClient` with your Chino.io `customer_id` to have access to the API.

There are two types of authentication that are supported:

### Customer credentials <!-- omit in toc -->
If you are using the API as an admin:

```python
from chino.api import ChinoAPIClient

chino = ChinoAPIClient("your-customer-id", customer_key="your-customer-key")
```

**NOTE**: if more than one auth method is defined, this one has the precedence.

### OAuth (Bearer Token) <!-- omit in toc -->
If you are using the API on behalf of a User that sent a `access_token`:

```python
from chino.api import ChinoAPIClient

chino = ChinoAPIClient("your-customer-id", access_token="user-access-token")
```

- - -

**Parameters**

-`customer_id` : the Customer ID of the Chino.io platform

-`customer_key` : (*optional*) one of the Customer Keys associated to your ID.

-`access_token`:  (*optional*) a OAuth Bearer Token sent by a user.

-`url`: the API URL you are targeting.
  Default is the **Production** API URL `https://api.chino.io/`.
  You can also use the **Sandbox** API URL `https://api.test.chino.io`.

-`version`: the version of the API. Currently we only have `v1`

-`timeout`: timeout for the requests in seconds, default is `30`.
  You'll get an exception if any API request takes longer to complete.
  
- `session`: Keep the connection open to improve performance. Default: `True`.
  [See section below](#requestssession----omit-in-toc---) to learn more.

#### requests.Session() <!-- omit in toc -->
This Python SDK uses the Python modules `requests` and relies on 
[`requests.Session()`](http://docs.python-requests.org/en/master/user/advanced/?highlight=session).

This solution keeps the connection to the Chino.io API open, to cut time overhead on multiple requests.
This translates to a *huge* improvement in performance (up to 4x faster).

If, for any reason, you want to disable this functionality, just set 
`session=False` when creating the `ChinoAPIClient()`

## SDK overview

### Authentication
Class that manages the auth, `chino.auth`. **In 99% of the cases this class does not need to be used.**

- `init`:
    -`customer_id` : the Customer ID of the Chino.io platform
    -`customer_key` : (*optional*) one of the Customer Keys associated to your ID
    -`access_token`:  (*optional*) a OAuth Bearer Token sent by a user.
**NOTE:  if `customer_key` is set, API calls are authenticated as admin (Customer). If `access_token` is set, the authentication is of a User.**
Admin has precedence in case both are set.
- `set_auth_admin` to set the auth as admin
- `set_auth_user` to set the auth as the user
- `get_auth` to get the Auth object

### User
Class to manage the user, `chino.users`

- `login`
- `current`
- `logout`
- `list`
- `detail`
- `create`
- `update`
- `partial_update`
- `delete`
- `search`: *new in ver 2.4.0* - [See example](#search-api)

### Group
`chino.groups`

- `list`
- `detail`
- `create`
- `update`
- `delete`
- `add_user`
- `del_user`

### Permission
`chino.permissions`

- `resources`
- `resource`
- `resource_children`
- `read_perms`
- `read_perms_doc`
- `read_perms_user`
- `read_perms_group`

### Repository
`chino.repotiories`

- `list`
- `detail`
- `create`
- `update`
- `delete`

### Schemas
`chino.schemas`

- `list`
- `create`
- `detail`
- `update`
- `delete`

### Document
`chino.documents`

- `list`
- `create`
- `detail`
- `update`
- `delete`
- `search`: *new in ver 2.4.0* - [See example](#search-api)

### BLOB
`chino.blobs`

- `send`: help function to upload a blob, returns `BlobDetail('bytes', 'blob_id', 'sha1', 'document_id', 'md5')`
- `start`
- `chunk`
- `commit`
- `detail`: returns `Blob(filename, content)`
- `delete`

### SEARCH (**deprecated**)
`chino.searches`

**This class has been deprecated and will be removed in version `3.0.0`** .

This class has been deprecated in favor of `documents.search()` and `users.search()`.

Refer to the [Search API](#search-api) section for details and examples.

### UserSchemas
`chino.user_schemas`

- `list`
- `create`
- `detail`
- `update`
- `delete`

### Collections
`chino.collections`

- `list`
- `create`
- `detail`
- `update`
- `delete`
- `list_documents`
- `add_document`
- `rm_document`
- `search`

### Consents (**deprecated**)
`chino.consents`

**This class has been deprecated and will be removed in version `3.0.0`** .

The Consent Management API is deprecated in favor of the new [Consenta API](https://docs.chino.io/consent/consentame/docs/v1).

## Features

### Resource IDs
each element has a `_id()` function that returns the `id` of the resource

### Response structure and pagination
The calls return Objects (see `object.py`) of the type of the call (e.g. `documents` return Documents) or raise an Exception if there's an error. Thus, you can catch the Exception in the code if something bad happens.
In case of `list` it returns a ListResult, which is composed of:
- `paging`:
    - `offest`: int
    - `count`: int
    - `total_count`: int
    - `limit`: int
- `documents` *(name of the object in plural)*: list *(the actual list of objects)*

All the objects - except `Blob` and `BlobDetail` - have:
- a method that converts them to a dict (`obj.to_dict()`)
- a property that returns the id of the resource (`obj._id`)

### List iteration
All the `Paginated Results` can be iterated using its returned object, example:
```python
repositories=chino.repositories.list()
for repo in repositories:
    print(repo)
```

### Search API
The new Search classes available from version `2.4.0` replace the `chino.searches` class - now deprecated.

For more information about our Search API, refer to our [API Docs](https://docs.chino.io/custodia/docs/v1#header-search-query).

Example:
```python
# query
query = {
  "and": [
    {"field": "my_string_field", "type": "eq", "value": "some_string"},
    {"field": "my_integer_field", "type": "lt", "value": 42},
  ]
}
# sort rules
sort =[
  {"field": "my_integer_field", "order": "desc"}
]

# Search Documents
chino.documents.search(schema_id, query=query, sort=sort)

# Search Users
chino.users.search(user_schema_id, query=query, sort=sort)
```

## SDK documentation
Not provided by defult, but can be compiled with [sphinx](sphinx-doc.org).

Requires the following packages:

    pip install sphinx-autobuild
    pip install sphinx-autodoc-annotation
    pip install sphinx-rtd-theme

## Contributing to the SDK

See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

#### Build for pip

    rm -r dist/*
    python setup.py bdist_wheel --universal
    twine upload dist/*
