# IP Fabric 

IPFabric is a Python module for connecting to and communicating against an IP Fabric instance.

## About

Founded in 2015, [IP Fabric](https://ipfabric.io/) develops network infrastructure visibility and analytics solution to
help enterprise network and security teams with network assurance and automation across multi-domain heterogeneous
environments. From in-depth discovery, through graph visualization, to packet walks and complete network history, IP
Fabric enables to confidently replace manual tasks necessary to handle growing network complexity driven by relentless
digital transformation. 

## v7.0.0 Deprecation Notices

In `ipfabric>=v7.0.0` the following will be deprecated:

- `ipfabric_diagrams` package will move to `ipfabric.diagrams`
- Python 3.7 support will be removed.
- The use of `token='<TOKEN>'` or `username='<USER>', password='<PASS>'` in `IPFClient()` will be removed:
  - Token: `IPFClient(auth='TOKEN')`
  - User/Pass: `IPFClient(auth=('USER', 'PASS'))`
  - `.env` file will only accept `IPF_TOKEN` or (`IPF_USERNAME` and `IPF_PASSWORD`) and not `auth`

## Versioning

Starting with IP Fabric version 5.0.x the python-ipfabric and python-ipfabric-diagrams will need to
match your IP Fabric version.  The API's are changing and instead of `api/v1` they will now be `api/v5.0`.

Version 5.1 will have backwards compatability with version 5.0 however 6.0 will not support any 5.x versions.
By ensuring that your ipfabric SDK's match your IP Fabric Major Version will ensure compatibility and will continue to work.

## Installation

```
pip install ipfabric
```

## Introduction

Please take a look at [API Programmability - Part 1: The Basics](https://ipfabric.io/blog/api-programmability-part-1/)
for instructions on creating an API token.

Most of the methods and features can be located in [Examples](examples) to show how to use this package. 
Another great introduction to this package can be found at [API Programmability - Part 2: Python](https://ipfabric.io/blog/api-programmability-python/)

## Diagrams

Diagramming in IP Fabric version v4.3 and above has been moved to it's own package.

Diagramming will move back to this project in v7.0

```
pip install ipfabric-diagrams
```

## Authentication
### Username/Password
Supply in client:
```python
from ipfabric import IPFClient
ipf = IPFClient('https://demo3.ipfabric.io/', auth=('user', 'pass'))
```

### Token
```python
from ipfabric import IPFClient
ipf = IPFClient('https://demo3.ipfabric.io/', auth='token')
```

### Environment 
The easiest way to use this package is with a `.env` file.  You can copy the sample and edit it with your environment variables. 

```commandline
cp sample.env .env
```

This contains the following variables which can also be set as environment variables instead of a .env file.
```
IPF_URL="https://demo3.ipfabric.io"
IPF_TOKEN=TOKEN
IPF_VERIFY=true
```

Or if using Username/Password:
```
IPF_URL="https://demo3.ipfabric.io"
IPF_USERNAME=USER
IPF_PASSWORD=PASS
```

## Development

### Poetry Installation

IPFabric uses [Poetry](https://pypi.org/project/poetry/) to make setting up a virtual environment with all dependencies
installed quick and easy.

Install poetry globally:
```
pip install poetry
```

To install a virtual environment run the following command in the root of this directory.

```
poetry install
```

To run examples, install extras:
```
poetry install ipfabric -E examples
```

### Test and Build

```
poetry run pytest
poetry build
```

Prior to pushing changes run:
```
poetry run black ipfabric
poetry update
```
