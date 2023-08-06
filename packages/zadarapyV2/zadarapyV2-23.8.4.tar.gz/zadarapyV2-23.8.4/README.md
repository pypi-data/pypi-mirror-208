# zadarapyV2

## Requirements.

Python 2.7 and 3.4+

## Installation & Usage
### pip install

Clone the repo and run:

```sh
make generate_pythons
```

from zadarapyV2 folder, run:

```sh
pip install -r requirements.txt
pip install .
```

Or install from devpi
```sh
pip install zadarapyv2 --index-url <devpi url> --trusted-host <devpi host name>
```

Or install from pypi
```sh
pip install zadarapyv2
```



Then import the package:
```python
import Vpsa, CommandCenter, ProvisioningPortal ,Zios
```

## Getting Started

```python
import Vpsa as vpsa
import CommandCenter as cc

vpsa_conf = vpsa.configuration.Configuration()
cc_conf = cc.configuration.Configuration()

# Configure host ip + basePath
vpsa_conf.host='http://10.2.10.33/api'

cc_conf.host = 'https://10.16.1.50/api/v2'

# Configure API key authorization: api_key
vpsa_conf.api_key = {'X-Access-Key':'PPYW8KNXJA495-2'}

# create an instance of the API class
vpsa_api = vpsa.ApiClient(vpsa_conf)

# Use Users api
vpsa_users_api = vpsa.UsersApi(vpsa_api)


try:
    api_response = vpsa_users_api.add_user(body_add_user=vpsa.BodyAddUser('john','john@mail.com'))
    pprint(api_response)
except ApiException as e:
    print("Exception when calling add_user: %s\n" % e)
try:
    users_list = vpsa_users_api.list_users().response.users
    pprint(users_list)
except ApiException as e:
    print("Exception when calling list_users: %s\n" % e)
```
