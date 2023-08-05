import argparse
import logging
import subprocess
from pydantic import BaseModel, parse_raw_as


class GLVariable(BaseModel):
    """Gitlab CI variable"""

    key: str
    value: str
    protected: bool
    variable_type: str = "env_var"
    masked: bool
    raw: bool
    environment_scope: str

    @property
    def gcl_type(self):
        """Type string to be used in YAML config"""
        return "variable" if self.variable_type == "env_var" else "file"


class GCLVariable(BaseModel):
    """Gitlab-CI-Local variable"""

    type: str
    values: dict[str, str]


class GLGroup(BaseModel):
    """Gitlab group"""

    id: int
    full_path: str


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
        ["glab", "variable", "export"], stderr=subprocess.PIPE, stdout=subprocess.PIPE
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


def main(target: str):
    if target != "gcl":
        logging.error(f"Target {target} is not supported.")
        exit(999)

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

    gcl_variables = convert_to_gcl(gl_variables)
    print_to_stdout(gcl_variables)


def cli():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Retrieve Gitlab CI variables and output yaml configuration contents for gitlab-ci-local"  # noqa: E501
    )
    parser.add_argument(
        "-t", "--target", default="gcl", help="CI/CD variable export target"
    )
    arguments = parser.parse_args()

    main(target=arguments.target)


if __name__ == "__main__":
    cli()
