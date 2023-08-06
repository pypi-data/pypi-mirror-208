# Copyright 2016 Brigham Young University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import click

from awsparams import __VERSION__, AWSParams


def sanity_check(param: str, force: bool) -> bool:
    if force:
        return True
    sanity_check = input(f"Remove {param} y/n ")
    return sanity_check == "y"


@click.group()
@click.version_option(version=__VERSION__)
def main():
    pass


@main.command("ls")
@click.argument("prefix", default="")
@click.option("--profile", type=click.STRING, help="profile to run with")
@click.option("--region", type=click.STRING, help="optional region to use")
@click.option("-v", "--values", is_flag=True, help="display values")
@click.option("-e", "--dot-env", is_flag=True, help="format list for a .env file")
@click.option("-t", "--tfvars", is_flag=True, help="format list for a .tfvars file")
@click.option("-r", "--jetbrains-run-config", is_flag=True, help="format list for a Jetbrains run configuration")
@click.option("-q", "--esc-quotes", is_flag=True, help="Escape quotes in values (for --env-vars or --tfvars)")
@click.option(
    "--decryption/--no-decryption",
    help="by default display decrypted values",
    default=True,
)
def ls(prefix="", profile="", region="", values=False, run_config=False, env_vars=False, tfvars=False, esc_quotes=False, decryption=True):
    """
    List Parameters, optionally matching a specific prefix
    """
    aws_params = AWSParams(profile, region)
    if run_config or env_vars or tfvars:  # all of these options should also fetch the values
        values = True
    if not values:
        decryption = False
    for parm in aws_params.get_all_parameters(
            prefix=prefix, values=values, decryption=decryption, trim_name=False
    ):
        if values:
            if run_config or env_vars or tfvars:
                param_parts = parm.Name.split('/')
                prefix_parts = prefix.split('/')
                # remove any duplicate, leading, or trailing delimiters from both lists
                for arr in [param_parts, prefix_parts]:
                    for part in arr:
                        if part == '':
                            arr.remove(part)
                name = []
                # 'subtract' the prefix from the name by starting from the rightmost element
                #  and appending elements leftwards until you reach the prefix
                for i in range(len(param_parts) - 1, len(prefix_parts) - 1, -1):
                    name.insert(0, param_parts[i])
                # reconstruct the param name
                name = '/'.join(name)
                """
                run_config - print out separated by '=' and ended with ';'
                env_vars - print out separated by '=', values wrapped in quotes
                tfvars - print out separated by ' = ', values wrapped in quotes
                """
                if env_vars:
                    click.echo(f"{name}=\"{escape_quotes(parm.Value) if esc_quotes else parm.Value}\"")
                elif tfvars:
                    click.echo(f"{name} = \"{escape_quotes(parm.Value) if esc_quotes else parm.Value}\"")
                elif run_config:
                    click.echo(f"{name}={parm.Value};")
            else:
                click.echo(f"{parm.Name}: {parm.Value}")
        else:
            click.echo(parm.Name)


def escape_quotes(string):
    newstr = ''
    for c in string:
        if c == '"':
            newstr += '\\"'
        else:
            newstr += c
    return newstr


@main.command("cp")
@click.argument("src")
@click.argument("dst", default="")
@click.option("--src_profile", type=click.STRING, default="", help="source profile")
@click.option(
    "--src_region", type=click.STRING, default="", help="optional source region"
)
@click.option(
    "--dst_profile", type=click.STRING, default="", help="destination profile"
)
@click.option(
    "--dst_region", type=click.STRING, default="", help="optional destination region"
)
@click.option("--prefix", is_flag=True, help="copy set of parameters based on a prefix")
@click.option("--overwrite", is_flag=True, help="overwrite existing parameters")
@click.option(
    "--key", type=click.STRING, default="", help="kms key to use for new copy"
)
def cp(
        src,
        dst,
        src_profile,
        src_region,
        dst_profile,
        dst_region,
        prefix=False,
        overwrite=False,
        key="",
):
    """
    Copy a parameter, optionally across accounts
    """
    aws_params = AWSParams(src_profile, src_region)
    # cross account copy without needing dst
    if dst_profile and src_profile != dst_profile and not dst:
        dst = src
    elif not dst:
        click.echo("dst (Destination) is required when not copying to another profile")
        return
    if prefix:
        params = aws_params.get_all_parameters(prefix=src, trim_name=False)
        for i in params:
            i = i._asdict()
            orignal_name = i["Name"]
            i["Name"] = i["Name"].replace(src, dst)
            if key:
                i["KeyId"] = key
            aws_params.put_parameter(
                i, overwrite=overwrite, profile=dst_profile, region=dst_region
            )
            click.echo(f'Copied {orignal_name} to {i["Name"]}')
        return True
    else:
        if isinstance(src, str):
            src_param = aws_params.get_parameter(src)
            if not src_param:
                click.echo(f"Parameter: {src} not found")
                return
            src_param = src_param._asdict()
            src_param["Name"] = dst
            if key:
                src_param["KeyId"] = key
            aws_params.put_parameter(
                src_param, overwrite=overwrite, profile=dst_profile, region=dst_region
            )
            click.echo(f"Copied {src} to {dst}")
            return True


@main.command("mv")
@click.argument("src")
@click.argument("dst")
@click.option("--prefix", is_flag=True, help="move/rename based on prefix")
@click.option("--profile", type=click.STRING, help="alternative profile to use")
@click.option("--region", type=click.STRING, help="alternative region to use")
@click.pass_context
def mv(ctx, src, dst, prefix=False, profile="", region=""):
    """
    Move or rename a parameter
    """
    if prefix:
        if ctx.invoke(
                cp, src=src, dst=dst, src_profile=profile, prefix=prefix, src_region=region
        ):
            ctx.invoke(
                rm, src=src, force=True, prefix=True, profile=profile, region=region
            )
    else:
        if ctx.invoke(cp, src=src, dst=dst, src_profile=profile, src_region=region):
            ctx.invoke(rm, src=src, force=True, profile=profile, region=region)


@main.command("rm")
@click.argument("src")
@click.option("-f", "--force", is_flag=True, help="force without confirmation")
@click.option("--prefix", is_flag=True, help="remove/delete based on prefix/path")
@click.option("--profile", type=click.STRING, help="alternative profile to use")
@click.option("--region", type=click.STRING, help="alternative region to use")
def rm(src, force=False, prefix=False, profile="", region=""):
    """
    Remove/Delete a parameter
    """
    aws_params = AWSParams(profile, region)
    if prefix:
        params = aws_params.get_all_parameters(prefix=src, trim_name=False)
        if len(params) == 0:
            click.echo(f"No parameters with the {src} prefix found")
        else:
            for param in params:
                if sanity_check(param.Name, force):
                    aws_params.remove_parameter(param.Name)
                    click.echo(f"The {param.Name} parameter has been removed")
    else:
        param = aws_params.get_parameter(name=src)
        if param and param.Name == src:
            if sanity_check(src, force):
                aws_params.remove_parameter(src)
                click.echo(f"The {src} parameter has been removed")
        else:
            click.echo(f"Parameter {src} not found")


@main.command("new")
@click.option(
    "--name", type=click.STRING, prompt="Parameter Name", help="parameter name"
)
@click.option("--value", type=click.STRING, help="parameter value")
@click.option(
    "--param_type",
    type=click.STRING,
    default="String",
    help="parameter type one of String(default), StringList, SecureString",
)
@click.option(
    "--key", type=click.STRING, default="", help="KMS Key used to encrypt the parameter"
)
@click.option(
    "--description", type=click.STRING, default="", help="parameter description text"
)
@click.option("--profile", type=click.STRING, help="alternative profile to be used")
@click.option("--region", type=click.STRING, help="alternative region to be used")
@click.option("--overwrite", is_flag=True, help="overwrite exisiting parameters")
def new(
        name=None,
        value=None,
        param_type="String",
        key="",
        description="",
        profile="",
        region="",
        overwrite=False,
):
    """
    Create a new parameter
    """
    AWSParams(profile, region).new_param(
        name,
        value,
        param_type=param_type,
        key=key,
        description=description,
        overwrite=overwrite,
    )


@main.command("set")
@click.argument("src")
@click.argument("value")
@click.option("--profile", type=click.STRING, default="", help="source profile")
@click.option("--region", type=click.STRING, default="", help="source region")
def set(src=None, value=None, profile="", region=""):
    """
    Edit an existing parameter
    """
    result = AWSParams(profile, region).set_param(src, value)
    if result:
        click.echo(f"updated param '{src}' with value")
    else:
        click.echo(f"not updated, param '{src}' already contains that value")


if __name__ == "__main__":
    main()
