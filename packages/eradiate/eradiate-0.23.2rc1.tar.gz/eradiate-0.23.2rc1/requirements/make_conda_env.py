import os
import sys
from copy import deepcopy

import click
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq as CS
from setuptools.config.pyprojecttoml import read_configuration


@click.command()
@click.option(
    "-s",
    "--sections",
    default="main,recommended,tests,dev,docs,production,optional",
    help="Dependency sections to include in the produced environment.yml file. "
    "Default: 'main,recommended,tests,dev,docs,production,optional'",
)
@click.option(
    "-i", "--input", default="pyproject.toml", help="Path to pyproject.toml file."
)
@click.option("-o", "--output", default=None, help="Path to output file.")
@click.option("-q", "--quiet", is_flag=True, help="Suppress terminal output.")
def cli(sections, input, output, quiet):
    """
    Create a Conda environment file from a pyproject.toml.
    """

    # Set YAML parameters
    yaml = YAML(typ="rt")  # Round-trip mode allows for comment insertion
    indent_offset = 2
    yaml.indent(offset=indent_offset)

    # Load environment file template
    with open(os.path.join("requirements", "environment.in")) as f:
        env_yml = yaml.load(f.read())

    # Extract dependency section contents
    if not quiet:
        print(f"Reading dependencies from {input}")

    setup_config = read_configuration(input)
    sections = [x.strip() for x in sections.split(",")]
    section_indices = dict()
    dep_list = deepcopy(env_yml["dependencies"]) if "dependencies" in env_yml else []
    i = len(dep_list)

    for section in sections:
        section_indices[section] = i

        try:
            packages = (
                setup_config["project"]["dependencies"]
                if section == "main"
                else setup_config["project"]["optional-dependencies"][section]
            )
        except KeyError:
            raise RuntimeError(f"Cannot fetch dependencies from {input}")

        mitsuba_pkg = None

        for package in packages:
            if package in dep_list:  # Do not duplicate
                continue
            # Temporary fix until an eradiate_mitsuba conda package is made available
            if "eradiate_mitsuba" in set(package.split("==") + package.split(">=") + package.split("<=") + package.split("!=")):
                mitsuba_pkg = package
                continue
            dep_list.append(package)
            i += 1

        if mitsuba_pkg:
            if "pip" not in dep_list:
                dep_list.append("pip")
            dep_list.append({"pip": [mitsuba_pkg]})

    # Format dependency list
    lst = CS(dep_list)

    for section, i in section_indices.items():
        lst.yaml_set_comment_before_after_key(i, section, indent_offset)

    env_yml["dependencies"] = lst

    # Output to terminal
    if not quiet:
        yaml.dump(env_yml, sys.stdout)

    # Output to file
    if output is not None:
        with open(output, "w") as outfile:
            if not quiet:
                print()
            print(f"Saving to {output}")
            yaml.dump(env_yml, outfile)


if __name__ == "__main__":
    cli()
