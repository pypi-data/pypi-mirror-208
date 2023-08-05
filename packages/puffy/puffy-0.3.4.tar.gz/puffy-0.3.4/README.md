# PUFFY

A collection of modules with zero-dependencies to help manage common programming tasks.

```
pip install puffy
```

Usage examples:

```python
from puffy.error import catch_errors

# This function will never fail. Instead, the error is safely caught.
@catch_errors
def fail():
    raise Exception("Failed")
    return "yes"

err, resp = fail() # `err` and `resp` are respectively None and Object when the function is successull. Otherwise, they are respectively StackedException and None.
```

```python
from puffy.object import JSON as js

obj = js({ 'hello':'world' })
obj['person']['name'] = 'Nic' # Notice it does not fail.
obj.s('address.line1', 'Magic street') # Sets obj.address.line1 to 'Magic street' and return 'Magic street'
```

# Table of contents

> * [APIs](#apis)
>	- [`error`](#error)
>		- [Basic `error` APIs - Getting in control of your errors](#basic-error-apis---getting-in-control-of-your-errors)
>		- [Nested errors and error stack](#nested-errors-and-error-stack)
>		- [Managing errors in `async/await` corountines](#managing-errors-in-asyncawait-corountines)
>   - [`log`](#log)
>       - [Basic `log` APIs](#basic-log-apis)
>       - [Logging errors](#logging-errors)
>       - [Environment variables](#environment-variables)
>	- [`object`](#object)
>		- [`JSON` API](#json-api)
> * [Dev](#dev)
>	- [Getting started](#dev---getting-started)
>	- [CLI commands](#cli-commands)
>	- [Install dependencies with `easypipinstall`](#install-dependencies-with-easypipinstall)
>	- [Linting, formatting and testing](#linting-formatting-and-testing)
>		- [Ignoring `flake8` errors](#ignoring-flake8-errors)
>		- [Skipping tests](#skipping-tests)
>		- [Executing a specific test only](#executing-a-specific-test-only)
>	- [Building and distributing this package](#building-and-distributing-this-package)
> * [FAQ](#faq)
> * [References](#references)
> * [License](#license)

# APIs
## `error`

The `error` module exposes the following APIs:
- `catch_errors`: A higher-order function that returns a function that always return a tuple `(error, response)`. If the `error` is `None`, then the function did not fail. Otherwise, it did and the `error` object can be used to build an error stack.
- `StackedException`: A class that inherits from `Exception`. Use it to stack errors.

### Basic `error` APIs - Getting in control of your errors

```python
from puffy.error import catch_errors

# This function will never fail. Instead, the error is safely caught.
@catch_errors
def fail():
    raise Exception("Failed")
    return "yes"

err, resp = fail() 

print(resp) # None
print(type(err)) # <class 'src.puffy.error.StackedException'> which inherits from Exception
print(str(err)) # Failed
print(len(err.stack)) # 1
print(str(err.stack[0])) # Failed
print(err.stack[0].__traceback__) # <traceback object at 0x7fc69066bf00>

# Use the `strinfigy` method to extract the full error stack details.
print(err.strinfigy()) 
# error: Failed
#   File "blablabla.py", line 72, in safe_exec
#     data = ffn(*args, **named_args)
#   File "blablabla.py", line 28, in fail
#     raise Exception("Failed")
```

### Nested errors and error stack

```python
from puffy.error import catch_errors, StackedException

# This function will never fail. Instead, the error is safely caught.
@catch_errors("Should fail")
def fail():
    err, resp = fail_again()
    if err:
        raise StackedException("As expected, it failed!", err) 
        # StackedException accepts an arbitrary number of inputs of type str or Exception:
        # 	- raise StackedException(err) 
        # 	- raise StackedException('This', 'is', 'a new error') 
    return "yes"

@catch_errors("Should fail again")
def fail_again():
    raise Exception("Failed again")
    return "yes"

err, resp = fail()

print(len(err.stack)) # 4
print(str(err.stack[0])) # Should fail
print(str(err.stack[1])) # As expected, it failed!
print(str(err.stack[2])) # Should fail again
print(str(err.stack[3])) # Failed again

# Use the `strinfigy` method to extract the full error stack details.
print(err.strinfigy()) 
# error: Should fail
#   File "blablabla.py", line 72, in fail
# error: As expected, it failed!
#   File "blablabla.py", line 72, in fail
# error: Should fail again
#   File "blablabla.py", line 72, in fail
# error: Failed again
#   File "blablabla.py", line 72, in safe_exec
#     data = ffn(*args, **named_args)
#   File "blablabla.py", line 28, in fail_again
#     raise Exception("Failed")
```

### Managing errors in `async/await` corountines

```python
from puffy.error import async_catch_errors
import asyncio

# This function will never fail. Instead, the error is safely caught.
@async_catch_errors
async def fail():
    await asyncio.sleep(0.01)
    raise Exception("Failed")
    return "yes"

loop = asyncio.get_event_loop()
err, resp = loop.run_until_complete(fail())

print(resp) # None
print(type(err)) # <class 'src.puffy.error.StackedException'> which inherits from Exception
print(str(err)) # Failed
print(len(err.stack)) # 1
print(str(err.stack[0])) # Failed
print(err.stack[0].__traceback__) # <traceback object at 0x7fc69066bf00>

# Use the `strinfigy` method to extract the full error stack details.
print(err.strinfigy()) 
# error: Failed
#   File "blablabla.py", line 72, in safe_exec
#     data = ffn(*args, **named_args)
#   File "blablabla.py", line 28, in fail
#     raise Exception("Failed")
```

## `log`
### Basic `log` APIs

This method prints a structured log to stdout. That structured log is a standard Python `dict` which is then serialized to `str` using `json.dumps`. This method is designed to never fail. It was originally designed to log messages to AWS CloudWatch.

```python
from puffy.log import log

log() # '{ "level":"INFO" }'

log(
    level="WARN", # Supported values: "INFO" (default), "WARN" (or "WARNING"), "ERROR", "CRITICAL"
    message="Seems drunk",
    code="drunky_drunky",
    metric=23,
    unit="beers", # Default is "ms" (i.e., milliseconds)
    data= {
        "name": "Dave",
        "age": 45
    },
    op_id= 12345,
    test=True
) # '{"level": "WARN", "message": "Seems drunk", "code": "drunky_drunky", "test": true, "metric": 23, "unit": "beers", "op_id": 12345, "data": {"name": "Dave", "age": 45}}'

# Logging time:
log(
    level="WARN", # Supported values: "INFO" (default), "WARN" (or "WARNING"), "ERROR", "CRITICAL"
    message="Seems drunk",
    code="drunky_drunky",
    time=34 # This is converted to the "metric" input with "unit" set to "ms" (cannot be overwritten)
) # '{"level": "WARN", "message": "Seems drunk", "code": "drunky_drunky", "metric": 34, "unit": "ms"}'
```

### Logging errors

The `log` API is designed to support puffy's `StackedException` errors. The advantage of using `StackedException` is that you can have confidence that the stacked errors are properly serialized (i.e., including message and traceback).

```python
from puffy.log import log
from puffy.error import catch_errors, StackedException as e

@catch_errors("Should fail")
def fail():
    err, resp = fail_again()
    if err:
        raise e(err)
    return "yes"

@catch_errors("Should fail again")
def fail_again():
    raise Exception("Failed again")
    return "yes"

err, *_ = fail()

# Supports `StackedException`
log(
    level="ERROR",
    errors=err) 
# '{"level": "INFO", "errors": "error: Should fail\n  File \"/Users/.../ur_code.py\", line 153, in fail\nerror: Should fail again\n  File \"/Users/.../ur_code.py\", line 153, in fail\nerror: Failed again\n  File \"/Users/.../ur_code.py\", line 112, in safe_exec\n    data = ffn(*args, **named_args)\n  File \"/Users/.../ur_code.py\", line 162, in fail_again\n    raise Exception(\"Failed again\")\n"}'

# Supports standard errors
log(
    level="ERROR",
    errors=Exception("Bim bam boom")) # '{"level": "ERROR", "errors": "Bim bam boom"}'

# Supports strings
log(
    level="ERROR",
    errors="Bim bam boom") # '{"level": "ERROR", "errors": "Bim bam boom"}'

# Supports list of errors
log(
    level="ERROR",
    errors=["Bim bam boom", Exception("Booom"), err]) # '{"level": "ERROR", "errors": "Bim bam boom\nBooom\nerror: Should fail\n  File \"/Users/.../ur_code.py\", line 153, in fail\nerror: Should fail again\n  File \"/Users/.../ur_code.py\", line 153, in fail\nerror: Failed again\n  File \"/Users/.../ur_code.py\", line 112, in safe_exec\n    data = ffn(*args, **named_args)\n  File \"/Users/.../ur_code.py\", line 162, in fail_again\n    raise Exception(\"Failed again\")\n"}'
```

### Environment variables

Often, specific common metadata must be added to all logs (e.g., server's details, api name, ...). For this purpose, use the `LOG_META` environment variable. This environment variable expects a stringified JSON object:

```python
from puffy.log import log

os.environ["LOG_META"] = json.dumps({"api_name": "hello"})

log(level="INFO", message="hello world") # '{"api_name": "hello", "level": "INFO", "message": "hello world"}'
```

## `object`
### `JSON` API

```python
from puffy.object import JSON as js

obj = js({ 'hello':'world' })
obj['person']['name'] = 'Nic' # Notice it does not fail.
obj.s('address.line1', 'Magic street') # Sets obj.address.line1 to 'Magic street' and return 'Magic street'

print(obj['person']['name']) # Nic
print(obj) # { 'hello':'world', 'person': { 'name': 'Nic' } }
print(obj.g('address.line1')) # Magic street
print(obj) # { 'hello':'world', 'person': { 'name': None }, 'address': { 'line1': 'Magic street' } }
print(obj.g('address.line2')) # Nonce
print(obj) # { 'hello':'world', 'person': { 'name': None }, 'address': { 'line1': 'Magic street', line2: None } }
```

# Dev
## Dev - Getting started

1. Clone this project:
```shell
git clone https://github.com/nicolasdao/pypuffy.git
```
2. Browse to the root folder:
```shell
cd pypuffy
```
3. Create a new virtual environment:
```shell
python3 -m venv .venv
```
4. Activate this virtual environment:
```shell
source .venv/bin/activate
```

To deactivate that virtual environment:
```shell
deactivate
```

## CLI commands

`make` commands:

| Command | Description |
|:--------|:------------|
| `python3 -m venv .venv` | Create a new virtual environment. |
| `source .venv/bin/activate` | Activate the virtual environment |
| `deactivate` | Deactivate the virtual environment |
| `make b` | Builds the package. |
| `make p` | Publish the package to https://pypi.org. |
| `make bp` | Builds the package and then publish it to https://pypi.org. |
| `make bi` | Builds the package and install it locally (`pip install -e .`). |
| `make install` | Install the dependencies defined in the `requirements.txt`. This file contains all the dependencies (i.e., both prod and dev). |
| `make install-prod` | Install the dependencies defined in the `prod-requirements.txt`. This file only contains the production dependencies. |
| `make n` | Starts a Jupyter notebook for this project. |
| `make t` | Formats, lints and then unit tests the project. |
| `make t testpath=<FULLY QUALIFIED TEST PATH>` | Foccuses the unit test on a specific test. For a concrete example, please refer to the [Executing a specific test only](#executing-a-specific-test-only) section. |
| `easyi numpy` | Instals `numpy` and update `setup.cfg`, `prod-requirements.txt` and `requirements.txt`. |
| `easyi flake8 -D` | Instals `flake8` and update `setup.cfg` and `requirements.txt`. |
| `easyu numpy` | Uninstals `numpy` and update `setup.cfg`, `prod-requirements.txt` and `requirements.txt`. |
| `easyv` | Returns the version defined in `setup.cfg`. |
| `easyv bump` | Bumps the patch version defined in `setup.cfg` (1).|
| `easyv bump minor` | Bumps the minor version defined in `setup.cfg` (1).|
| `easyv bump major` | Bumps the major version defined in `setup.cfg` (1).|
| `easyv bump x.x.x` | Sets the version defined in `setup.cfg` to x.x.x (1).|

> __(1):__ Bumping a version using `easyv` can apply up to three updates:
>1. Updates the version property in the `setup.cfg` file.
>2. If the project is under source control with git and git is installed:
>   1. Updates the `CHANGELOG.md` file using the commit messages between the current branch and the last version tag. If the `CHANGELOG.md` file does not exist, it is automatically created.
>   2. git commit and tag (using the version number prefixed with `v`) the project.

## Install dependencies with `easypipinstall`

`easypipinstall` adds three new CLI utilities: `easyi` (install) `easyu` (uninstall) and `easyv` (manages package's version). To learn the full details about `easypipinstall`, please refer to https://github.com/nicolasdao/easypipinstall.

Examples:
```
easyi numpy
```

This installs `numpy` (via `pip install`) then automatically updates the following files:
- `setup.cfg` (WARNING: this file must already exists):
	```
	[options]
	install_requires = 
		numpy
	```
- `requirements.txt` and `prod-requirements.txt`

```
easyi flake8 black -D
```

This installs `flake8` and `black` (via `pip install`) then automatically updates the following files:
- `setup.cfg` (WARNING: this file must already exists):
	```
	[options.extras_require]
	dev = 
		black
		flake8
	```
- `requirements.txt` only, as those dependencies are installed for development purposes only.

```
easyu flake8
```

This uninstalls `flake8` as well as all its dependencies. Those dependencies are uninstalled only if they are not used by other project dependencies. The `setup.cfg` and `requirements.txt` are automatically updated accordingly.

## Linting, formatting and testing

```
make t
```

This command runs the following three python executables:

```
black ./
flake8 ./
pytest --capture=no --verbose $(testpath)
```

- `black` formats all the `.py` files, while `flake8` lints them. 
- `black` is configured in the `pyproject.toml` file under the `[tool.black]` section.
- `flake8` is configured in the `setup.cfg` file under the `[flake8]` section.
- `pytest` runs all the `.py` files located under the `tests` folder. The meaning of each option is as follow:
	- `--capture=no` allows the `print` function to send outputs to the terminal. 
	- `--verbose` displays each test. Without it, the terminal would only display the count of how many passed and failed.
	- `$(testpath)` references the `testpath` variable. This variable is set to `tests` (i.e., the `tests` folder) by default. This allows to override this default variable with something else (e.g., a specific test to only run that one).

### Ignoring `flake8` errors

This project is pre-configured to ignore certain `flake8` errors. To add or remove `flake8` errors, update the `extend-ignore` property under the `[flake8]` section in the `setup.cfg` file.

### Skipping tests

In your test file, add the `@pytest.mark.skip()` decorator. For example:

```python
import pytest

@pytest.mark.skip()
def test_self_describing_another_test_name():
	# ... your test here
```

### Executing a specific test only

One of the output of the `make t` command is list of all the test that were run (PASSED and FAILED). For example:

```
tests/error/test_catch_errors.py::test_catch_errors_basic PASSED
tests/error/test_catch_errors.py::test_catch_errors_wrapped PASSED
tests/error/test_catch_errors.py::test_catch_errors_nested_errors PASSED
tests/error/test_catch_errors.py::test_catch_errors_StackedException_arbitrary_inputs FAILED
```

To execute a specific test only, add the `testpath` option with the test path. For example, to execute the only FAILED test in the example above, run this command:

```
make t testpath=tests/error/test_catch_errors.py::test_catch_errors_StackedException_arbitrary_inputs
```

## Building and distributing this package

1. Make sure the test and lint operations have not produced errors:
```shell
make t
```
2. Version and tag this package using one of the following commands (1):
    - `easyv bump`: Use this to bump the patch version.
    - `easyv bump minor`: Use this to bump the minor version.
    - `easyv bump major`: Use this to bump the major version.
    - `easyv bump x.x.x`: Use this to bump the version to a specific value.
3. Push those latest changes to your source control repository (incl. tags). For example:
```shell
git push origin master --follow-tags
```
4. Build this package:
```shell
make b
```
> This command is a wrapper around `python3 -m build`.
5. Publish this package to https://pypi.org:
```shell
make p
```
> This command is a wrapper around the following commands: `python3 -m build; twine upload dist/*`


To test your package locally before deploying it to https://pypi.org, you can run build and install it locally with this command:

```shell
make bi
```

This command buils the package and follows with `pip install -e .`.

> (1): This step applies three updates:
> 1. Updates the version property in the `setup.cfg` file.
> 2. Updates the `CHANGELOG.md` file using the commit messages between the current branch and the last version tag.
> 3. git commit and tag (using the version number prefixed with `v`) the project.

# FAQ

# References

# License

BSD 3-Clause License

```
Copyright (c) 2019-2023, Cloudless Consulting Pty Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

