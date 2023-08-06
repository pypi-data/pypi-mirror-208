import argparse
import logging
import subprocess
from typing import Iterable
from pydantic import parse_raw_as
from variables import GCLVariable, GLGroup, GLVariable
from targets import Target
from pathlib import Path


def convert_to_gcl(ci_variables: list[GLVariable]):
    """Collect CI variables into a new structure."""
    gcl_variables: dict[str, GCLVariable] = {}
    for ci_variable in ci_variables:
        environment_values = {ci_variable.environment_scope: ci_variable.value}
        if (gcl_variable := gcl_variables.get(ci_variable.key, None)) is None:
            # Create a new variable
            gcl_variable = GCLVariable(
                type=ci_variable.gcl_type, values=environment_values
            )
            gcl_variables[ci_variable.key] = gcl_variable
        else:
            # Append to existing variable new environment-specific value

            # WARNING: here we use dictionary updating, which implicitly makes use
            # of the rule that if an environment already has a value, it will be
            # updated with a new value from the current `ci_variable`.
            # The list `ci_variables` is sorted by groups (top-level first) -> project
            # so that the CI variables are overwritten according to the usual scoping
            # rules
            values = {**gcl_variable.values, **environment_values}
            gcl_variable.values = values

        # Store GCL variable
        gcl_variables[ci_variable.key] = gcl_variable
    return gcl_variables


def print_to_stdout(gcl_variables) -> None:
    """Print to stdout the contents of .gitlab-ci-local-variables.yml"""
    print("---")
    for name, gcl_variable in gcl_variables.items():
        print(f"{name}:")
        print(f"{' '*2}type: {gcl_variable.type}")
        print(f"{' '*2}values:")
        for environment_scope, environment_value in gcl_variable.values.items():
            if gcl_variable.type == "file":
                print(f"{' '*4}'{environment_scope}': |")
                for line in environment_value.split("\n"):
                    print(f"{' '*6}{line}")
            else:
                print(f"{' '*4}'{environment_scope}': '{environment_value}'")


def is_glab_installed() -> bool:
    """Return True if `glab` is installed, otherwise return False"""
    process = subprocess.run(["which", "glab"], stdout=subprocess.DEVNULL)

    if (return_code := process.returncode == 0) is False:
        logging.error("You must install the Gitlab CLI for glab2gcl to work.")

    return return_code


def is_glab_authenticated() -> bool:
    """Return True if `glab` is authenticated, otherwise return False."""
    # Catch output from stderrr; glab writes to stderr even when authenticated
    process = subprocess.run(["glab", "auth", "status"], stderr=subprocess.PIPE)
    if (return_code := b"Logged in to" in process.stderr) is False:
        logging.error(
            "The `glab` client is not authenticated. Authenticate using `glab auth login`"  # noqa: E501
        )

    return return_code


def export_variables(process) -> list[GLVariable]:
    """Return"""
    if process.returncode == 1:
        logging.error(
            "Not inside a git repository or remote Gitlab missing. You must run `glab2gcl` inside git repository that has a Gitlab remote."  # noqa: E501
        )
        # ERROR
        exit(3)

    # Return an empty list if no variables are present
    if not process.stdout:
        return []

    return parse_raw_as(list[GLVariable], process.stdout)


def export_project_variables() -> list[GLVariable]:
    """Export project variables"""
    process = subprocess.run(
        ["glab", "variable", "export", "-R", "42analytics1/experiments/gitlab-to-gcl"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    return export_variables(process)


def export_group_variables(group_path: str) -> list[GLVariable]:
    """Export group variables"""
    process = subprocess.run(
        ["glab", "variable", "export", "--group", group_path],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    return export_variables(process)


def get_project_groups() -> list[GLGroup]:
    """Return a list of Gitlab groups, sorted top-level first"""
    process = subprocess.run(
        ["glab", "api", "projects/:id/groups"], stdout=subprocess.PIPE
    )
    if process.returncode == 1:
        logging.error("Error retrieving groups: {subprocess.stdout.read()}")

    return sorted(
        parse_raw_as(list[GLGroup], process.stdout),
        key=lambda x: len(x.full_path.split("/")),
    )


def convert_to_env(env_path: Path, gl_variables: Iterable[GLVariable]) -> None:
    """Return GL variables"""

    filenames = set()

    for gl_variable in gl_variables:
        if gl_variable.gcl_type == "variable":
            # The .env file to write to is '.env[.<environment_scope>]', where the scope
            # is added if the scope is anything other than '*'
            filename = ".env"
            if gl_variable.environment_scope != "*":
                filename = f"{filename}.{gl_variable.environment_scope}"

            file_access = "w" if filename not in filenames else "a"
            with open(env_path / filename, file_access) as f:
                f.write(f"{gl_variable.key}='{gl_variable.value}'\n")

            # Add the filename
            filenames.add(filename)

        elif gl_variable.gcl_type == "file":
            # Write the contents of file-type variables to a file
            filename = f"{gl_variable.key.lower()}"
            if gl_variable.environment_scope != "*":
                filename = f"{filename}.{gl_variable.environment_scope}"
            with open(env_path / filename, "w") as f:
                f.write(gl_variable.value)


def main(target: Target, env_path: Path):
    if not is_glab_installed():
        # ERROR CODE 1: Gitlab CLI (`glab`) is not installed or found on PATH
        exit(1)

    if not is_glab_authenticated():
        # ERROR CODE 2: Gitlab CLI (`glab`) is not authenticated
        exit(2)

    gl_variables: list[GLVariable] = []

    project_groups = get_project_groups()
    for project_group in project_groups:
        group_variables = export_group_variables(group_path=project_group.full_path)
        gl_variables.extend(group_variables)

    # Obtain variables
    project_variables = export_project_variables()
    gl_variables.extend(project_variables)

    match target:
        case Target.GCL:
            gcl_variables = convert_to_gcl(gl_variables)
            print_to_stdout(gcl_variables)
        case Target.ENV:
            if not env_path.exists():
                env_path.mkdir(parents=True)

            convert_to_env(env_path=env_path, gl_variables=gl_variables)
        case _:
            raise NotImplementedError()


def cli():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Retrieve Gitlab CI variables and output yaml configuration contents for gitlab-ci-local"  # noqa: E501
    )
    parser.add_argument(
        "-t",
        "--target",
        type=Target,
        default="env",
        help="CI/CD variable export target",
    )
    parser.add_argument(
        "-e",
        "--env-path",
        type=Path,
        default=".gitlab",
        help="Output path when --target ENV is passed",
    )
    arguments = parser.parse_args()

    main(target=arguments.target, env_path=arguments.env_path)


if __name__ == "__main__":
    cli()
