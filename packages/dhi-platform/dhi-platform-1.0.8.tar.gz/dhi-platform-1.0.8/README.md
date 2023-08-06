<img src="http://dhigroup.com/-/media/shared%20content/global/global%20repository/logos/dhi/dhi_logo_pos_rgb_nomargin.png?h=61&la=en&w=94" alt="DHI"/>


MIKE Cloud Platform SDK for Python
==================================


What is MIKE Cloud Platform SDK for Python?
-------------------------------------------

MIKE Cloud Platform SDK for Python allows you to programmatically access MIKE Cloud Platform from Python.
It also includes set of CLI tools to manipulate data and access services in MIKE Cloud Platform.

Here is a small example:

```bash
plt cfg login --login
plt prj create --name "My project"
plt prj ls
```
See [the documentation](https://develop.mike-cloud.com/Sdk.html) for more examples.

MIKE Cloud Platform SDK for Python is in development; some features are missing and there could be even bugs :-o


Requirements
------------

You need Python 3.8 or later.
In Ubuntu, Mint and Debian you can install Python 3 like this:

    $ sudo apt-get install python3 python3-pip python3-wheel python3-cffi python3-cryptography python3-greenlet python3-gevent python3-yaml

In Alpine:

    $ apk add --no-cache bash python3 py3-pip py3-wheel py3-cffi py3-cryptography py3-greenlet py3-gevent py3-yaml

For other Linux flavors, macOS and Windows, packages are available at

  https://www.python.org/getit/


Quick start
-----------

MIKE Cloud Platform SDK for Python and additional packages are installed using pip:

    $ pip install -U dhi-platform


If you want to run the latest stable version of the code, you can install from git:

    $ pip install -U azure-identity azure-storage-blob signalrcore signalr-async PyYAML
    $ pip install -U git+https://dhigroup@dev.azure.com/dhigroup/MIKE/_git/mike-platform-sdk-py@master


Or if you want to run the latest development (unstable) version of the code from git:

    $ pip install -U azure-identity azure-storage-blob signalrcore signalr-async PyYAML
    $ pip install -U git+https://dhigroup@dev.azure.com/dhigroup/MIKE/_git/mike-platform-sdk-py@develop


Manual installation: get files from mike-platform-sdk-py repository (https://dhigroup@dev.azure.com/dhigroup/MIKE/_git/mike-platform-sdk-py). Add "src" directory to PYTHONPATH and "bin" directory to PATH. Install additional packages: azure-identity, azure-storage-blob, signalrcore, signalr-async and PyYAML:

    $ pip install -U azure-identity azure-storage-blob signalrcore signalr-async PyYAML


Now, if Python on your system is configured properly (else see
"Troubleshooting" below) you can try CLI commands.
Please note that this example will try to use interactive authentication.
It opens a browser to interactively authenticate a user on *Windows* operating systems
or it authenticates users through the device code flow on *Linux* systems:

```bash
plt
plt cfg
plt cfg login -h
plt cfg login --login
plt prj create --name "My project"
plt prj ls -v
# switch to DEV environment
plt cfg login --login -e dev
plt prj ls -v
# back to PROD environment
plt prj ls -v -e prod
```

## How to authenticate in Python

When creating MIKE Cloud Platform clients in Python, you must provide credentials. There are two ways to do that:

1. Using open api key

Provided you know your customer ID and that  you have a valid api key assigned to a project, you can create an identity and provide that to clients. Open API key for the MIKE CLoud Platform can be requested through mike@dhigroup.com and assigned to projects using Data Admin UI application.

Example:
```py
from dhi.platform.authentication import ApiKeyIdentity
from dhi.platform.metadata import MetadataClient
key = "<api key uuid>"
identity = ApiKeyIdentity(apikey=key)
client = MetadataClient(identity=identity)
```

If you want to target a different environment than production, provide the optional `environment` parameter.

2. Using interactive user login

If you are an onboarded user, you can login interactively in a web browser.

Example:
```py
from dhi.platform.authentication import InteractiveIdentity
from dhi.platform.metadata import MetadataClient
identity = InteractiveIdentity()
client = MetadataClient(identity=identity)
```

If you want to target a different environment than production, provide the optional `environment` parameter.
If you want to use account from the last login, use `forcelogin=False` (optional, default is `forcelogin=True`):
```py
identity = InteractiveIdentity(environment="test", forcelogin=False)
```


Web site and documentation
--------------------------

Documentation and additional information is available at the web site:

  https://develop.mike-cloud.com

Or you can jump straight to the documentation:

  https://develop.mike-cloud.com/docs/


Troubleshooting
---------------

Depending on your configuration, you may have to run `pip` like this:

    $ pip install --no-deps -U dhi-platform

This doesn't automatically install the appropriate version of
azure-identity, azure-storage-blob, signalrcore, signalr-async and PyYAML.
You can install them manually:

    $ pip install -U azure-identity azure-storage-blob signalrcore signalr-async PyYAML

If the `plt` command isn't found after installation: After
`pip install`, the `plt` script and
dependencies, will be installed to system-dependent locations.
Sometimes the script directory will not
be in `PATH`, and you have to add the target directory to `PATH`
manually or create a symbolic link to the script.  In particular, on
macOS, the script may be installed under `/Library/Frameworks`:

    /Library/Frameworks/Python.framework/Versions/<version>/bin

In Windows, the script is generally installed in
`\PythonNN\Scripts`. So, type check a program like this (replace
`\Python38` with your Python installation path):

    C:\>\Python38\python \Python38\Scripts\plt ...

### Working with `virtualenv`

If you are using [`virtualenv`](https://virtualenv.pypa.io/en/stable/),
make sure you are running a python3 environment. Installing via `pip3`
in a v2 environment will not configure the environment to run installed
modules from the command line.

    $ pip install -U virtualenv
    $ python3 -m virtualenv env


Development status
------------------

MIKE Cloud Platform SDK for Python is beta software.


Changelog
---------


Issue tracker
-------------


License
-------

MIKE Cloud Platform SDK for Python is licensed under the terms of the MIT License (see the file
LICENSE).