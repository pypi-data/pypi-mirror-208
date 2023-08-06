# Note
Version 1 of this library is drastically different than previous versions.
The CLI Application hasn't changed but the library it uses has.
Please pay extra attention to the examples below or look at the underlying class for more information.

# Why this script?

The current (Jul 2017) AWS Console for the Systems Manager Parameter
Store is good for adding and editing the values of parameters, but
misses key productivity functions like copying (especially en mass),
renaming, etc. The current `aws ssm` CLI is very similar in
functionality to the AWS Console.

This script is to automate a lot of the manual work currently needed
with the existing AWS-provided UIs.

# Docs
Full documentation can be found here: https://awsparams.readthedocs.io/en/latest/

# Installation

  - AWSParams requires Python 3.6+
  - Depending on your Python3.6 install either `pip install awsparams` or `pip3 install awsparams`
    - If you're on windows, make sure that `C:\Users\{your user}\AppData\Roaming\Python\{your python version}\Scripts` has been added to your user path.

# Usage
## Library:

```python
from awsparams import AWSParams
 
# Using default Profile
aws_params = AWSParams()

# Using a Custome Profile
aws_params = AWSParams('MyProfile')

#get a single parameter
param = get_parameter('test1')
# ParamResult(Name='test1', Value='test123', Type='SecureString')

#ParamResult is a named tuple with properties Name, Value, Type
param.Name # 'test1'
param.Value # 'test123'
param.Type # 'SecureString'

# get multiple parameters with a prefix
params = get_all_parameters(prefix="testing.testing.")
# [ParamResult(Name='testing', Value='1234', Type='String'),
#  ParamResult(Name='testing2', Value='1234', Type='String')]

# get multiple parameters by path
params = get_all_parameters(prefix="/testing/testing/", by_path=True)
# [ParamResult(Name='testing', Value='1234', Type='String'),
#  ParamResult(Name='testing2', Value='1234', Type='String')]

# get multiple parameters by path
params = get_all_parameters(prefix="/testing/testing/", by_path=True, trim_name=False)
# [ParamResult(Name='/testing/testing/testing', Value='1234', Type='String'),
#  ParamResult(Name='/testing/testing/testing2', Value='1234', Type='String')]

# get just a parameter value
value = get_parameter_value('test1')
# test123
```
For more detailed examples of usage as a library see the cli implementation [here](https://github.com/byu-oit/awsparams/blob/master/awsparams/cli.py).

## CLI application:
Usage can be referenced by running `awsparams --help` or `awsparams
subcommand --help` commands:

    Usage: awsparams [OPTIONS] COMMAND [ARGS]...
    
    Options:
    --version  Show the version and exit.
    --help     Show this message and exit.
    
    Commands:
    cp   Copy a parameter, optionally across accounts
    ls   List Paramters, optional matching a specific...
    mv   Move or rename a parameter
    new  Create a new parameter
    rm   Remove/Delete a parameter
    set  Edit an existing parameter

# Command Examples

## ls usage

ls names only: `awsparams ls`

ls with values no decryption: `awsparams ls --values` or `awsparams ls -v`

ls with values and decryption: `awsparams ls --with-decryption`

ls by prefix: `awsparams ls appname.prd`

ls with values, formatted for using in a Jetbrains run configuration: `awsparams ls -r <prefix>`
or `awsparams ls --jetbrains-run-config <prefix>`

ls with values, formatted for using in a `.env` file: `awsparams ls -e <prefix>`
or `awsparams ls --dot-env <prefix>`

ls with values, formatted for using in a `.tfvars` file: `awsparams ls -t <prefix>`
or `awsparams ls --tfvars <prefix>`

For the above two options, add the `-q` or `--esc-quotes` flag for adding `\` in front of any quotation marks in
the values, such as in stringify-ed JSON objects. Most `.env` file parsers don't require this, but `.tfvars`
probably does.

## new usage

new interactively: `awsparams new`

new semi-interactively: `awsparams new --name appname.prd.username`

new non-interactive: `awsparams new --name appname.prd.usrname --value parameter_value
--description parameter_descripton`

## cp usage

copy a parameter: `awsparams cp appname.prd.username newappname.prd.username`

copy set of parameters with prefix appname.dev. to appname.prd.: `awsparams cp appname.dev. appname.prd. --prefix`

copy set of parameters starting with prefix repometa-generator.prd
overwrite existing parameters accross different accounts: `awsparams cp repometa-generator.prd --src_profile=dev --dst_profile=trn
--prefix=True`

copy single parameters accross different accounts: `awsparams cp appname.dev.username appname.trb.us`
