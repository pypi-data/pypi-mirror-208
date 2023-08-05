# Glabvars

A Python wrapper for retrieving Gitlab Ci/CD variables to enable injecting them into locally running GitLab CI/CD pipelines run with `gitlab-ci-local`.

Features:
- Retrieve [project-level CI/CD variables](https://docs.gitlab.com/ee/ci/variables/#for-a-project)
- Retrieve (inherited) [group-level CI/CD variables](https://docs.gitlab.com/ee/ci/variables/#for-a-group)
- Support for [environment-scoped CI/CD variables](https://docs.gitlab.com/ee/ci/environments/#limit-the-environment-scope-of-a-cicd-variable)
- Support variable-type (normal) and [file-type CI/CD variables](https://docs.gitlab.com/ee/ci/variables/#use-file-type-cicd-variables)
- Export to `gitlab-ci-local` YAML configuration file

# Usage

Run the `glabvars` CLI app inside a git repository with a Gitlab remote.
The application can return a YAML configuration string for `gitlab-ci-local` to `stdout`.
You can pipe this output to `.gitlab-ci-local-variables.yml` so that `gitlab-ci-local` can use the variables.
```shell
glabvars --target gcl > .gitlab-ci-local-variables.yml
```

# Installation
Install with `pip` to install globally:

```shell
pip install glabvars
```

Or alternatively with `pipx` to isolate dependencies of `glabvars` from other globally installed Python apps (requires `pipx`):
```shell
pipx install glabvars
```

# Requirements
You must have [`glab`](https://gitlab.com/gitlab-org/cli) installed and be authenticated with the relevant Gitlab instance to retrieve the CI/CD variables.
Check whether you are authenticated by calling `glab auth status`.

# Future work
Make it extensible to other targets.
