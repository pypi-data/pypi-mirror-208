# Chino Python SDK <!-- omit in toc -->

**Official Python SDK** for Chino.io API

**Version**: `2.12.0`
 
**Useful links**
 - [Full SDK instructions](./INSTRUCTIONS.md)
 - [Chino.io API docs](https://docs.test.chino.io/custodia/docs/v1)
 - [chino-python on PyPi](https://pypi.org/project/chino/)

For issues or questions, please contact [tech-support@chino.io](mailto:tech-support@chino.io).

--------------------------------------------------------------------------------------------------------
#### Table of content <!-- omit in toc -->

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage example](#usage-example)
  - [Example: create a Repository](#example-create-a-repository)

--------------------------------------------------------------------------------------------------------

## Requirements
Python 3 and pip

## Installation
You can install from pip:

    pip install chino

## Usage example
To use the SDK you will need a Chino.io account. Create one at https://console.test.chino.io

To perform API calls using the SDK, create an instance the `ChinoApiClient`.

**Customer credentials**

If you are using the API as an admin:

```python
from chino.api import ChinoAPIClient
chino = ChinoAPIClient("your-customer-id", customer_key="your-customer-key")
```

**OAuth (Bearer Token)**

If you are using the API on behalf of a User that sent a `access_token`:

```python
from chino.api import ChinoAPIClient
chino = ChinoAPIClient("your-customer-id", access_token="user-access-token")
```

### Example: create a Repository

```python
>>> from chino.api import ChinoAPIClient
>>> chino = ChinoAPIClient("your-customer-id", customer_key="your-customer-key", url="https://api.test.chino.io")
>>> r = chino.repositories.create("My first repository")
>>> print(r.description)
'My first repository'
```

*Learn more about the SDK in the [full reference](./INSTRUCTIONS.md).*
