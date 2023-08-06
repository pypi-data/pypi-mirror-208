# xrpl-nocode-automation
This repository contains code which allows users to run automated XRPL tests on different networks. It also generates a python package named 'claudia', which can be installed from [PyPi](https://test.pypi.org/project/claudia/).

---

## General prerequisites
Please have the following installed on your machine before proceeding further:
- [Python3](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
-  Following is only required if you intend to run Javascript tests.
   - [node](https://nodejs.org/en/download)
   - [npm](https://www.npmjs.com/package/download)

---

## Build Rippled
    More information coming soon...
---

## Launch Local Network
    More information coming soon...
---

## How to run the tests?
This section contains instructions for running the tests either directly using both `claudia` and the codebase directly.


### Run tests using claudia
 - Install claudia from [PyPi](https://test.pypi.org/project/claudia/), using the following command:
   
        pip install -i https://test.pypi.org/simple/ claudia
 - From your terminal, run: `claudia`
   - Use `--help` option with the CLI to view supported options.
   - Example Usage:
     - `claudia build`: Builds rippled locally.
     - `claudia network`: Launches local network using Rippled. Needs access to built rippled.
     - `claudia run python`: Runs Python tests on local network. Use `--help` to view other supported options. 
     - `claudia run javascript`: Runs Javascript tests on local network. Use `--help` to view other supported options. 

### Run tests using the codebase instead of using claudia
- Clone this [repo](https://gitlab.ops.ripple.com/xrpledger/xrpl-nocode-automation)
- Navigate to `src/claudia/python` or `src/claudia/javascript` folder, depending on which tests you wish to run.
- Run `./runSetup`. This is a one time step and does not need to be repeated each time.
- Run the tests:
  - If you wish to run the tests on a local network, run `./runTest`. Please view [Local Network](#launch-local-network) to launch a local network.
  - If you wish to run the tests on different networks, use `./runTest --help` flag to see more options.
---

### How to publish claudia to PyPi?
- Create an account with PyPi, if you don't have one. Verify the email.
- Clone this [repo](https://gitlab.ops.ripple.com/xrpledger/xrpl-nocode-automation)
- Install/update pip, if needed:
  
        python3 -m pip install --upgrade pip
- Install /update setuptools, if needed.
  
        pip install --upgrade setuptools
- Increment the version in [setup.py](https://gitlab.ops.ripple.com/xrpledger/xrpl-nocode-automation/-/blob/ksaxena/initial_commit/setup.py#L8)
- Remove any previous builds using the following command:
  
        rm -fr build/ dist/ claudia.egg-info
- Generate the package locally using the following command:

        python3 setup.py sdist bdist_wheel

- Upload the package to PyPi, using the following command (you will need to enter your PyPi credentials):
        
        python3 -m twine upload --verbose --repository testpypi dist/*
