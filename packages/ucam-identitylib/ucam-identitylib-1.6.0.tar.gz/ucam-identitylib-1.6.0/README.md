# Identity Lib

This Python package contains shared code related to Identity systems within UIS. It's primary
purpose is to encourage code-reuse and to allow for client systems to make use of the same
data structures and logic that is contained within our emergent identity APIs.

## Use

Install `ucam-identitylib` using pip:

```
pip install ucam-identitylib
```

The module can then be used as `identitylib`:

```python3
from identitylib.identifiers import Identifier

identifier = Identifier.from_string('wgd23@v1.person.identifiers.cam.ac.uk')
print(identifier)
```

## Developer quickstart

This project contains a dockerized testing environment which wraps [tox](https://tox.readthedocs.io/en/latest/).

Tests can be run using the `./test.sh` command:

```bash
# Run all PyTest tests and Flake8 checks
$ ./test.sh

# Run PyTest and Flake8 and recreate test environments
$ ./test.sh --recreate

# Run just PyTest
$ ./test.sh -e py3

# Run a single test file within PyTest
$ ./test.sh -e py3 -- tests/test_identifiers.py

# Run a single test file within PyTest with verbose logging
$ ./test.sh -e py3 -- tests/test_identifiers.py -vvv
```

### Pulling latest specs from source repositories

Local copies of the OpenAPI specs used to generate the library should be pulled in to this repo
so the specific specs used in each build are under revision control. This can be done using the
provided script:

```bash
$ ./pull-specs.sh

# If an access token required for https clones from gitlab repositories
# then this can be specified using:
$ ./pull-specs.sh --token "ACCESS_TOKEN_HERE"

# You may need to first set the $USER environment variable to match the GitLab account name.

```

### Generating the identitylib

The identitylib is generated during the docker build process. To create a local copy of the
identitylib distribution use the build script:

```bash
$ ./build-local.sh
```

This will create a new folder `/dist` in the current directory with the wheel and tar package for
identitylib.
