# Contributing

## Local development

### Create a virtual environment

Ensure one of the supported Pythons (see [`pyproject.toml`]) is installed
and used by the `python3` executable:

[`pyproject.toml`]: ./pyproject.toml

```sh
python3 --version
```

Then create and activate a virtual environment.
If you don't have any other way of managing virtual environments
this can be done by running:

```sh
python3 -m venv venv
source venv/bin/activate
```

You could also use [virtualenvwrapper], [direnv] or any similar tool
to help manage your virtual environments.

### Install the Python dependencies

To install all the development dependencies in your virtual environment,
run:

```sh
python3 -m pip install -r requirements.txt
```

[direnv]: https://direnv.net
[virtualenvwrapper]: https://virtualenvwrapper.readthedocs.io/

The tools used to manage this project will be installed.

### Run the tests

To start the tests with [tox](https://tox.wiki), run:

```sh
tox
```

Alternatively, if you want to run the tests directly in your virtual environment,
you many run the tests with:

```sh
PYTHONPATH=src python3 -m pytest
```

### Static analysis

Run all static analysis tools with [`pre-commit`](https://pre-commit.com):

```sh
pre-commit run --all-files
```

You can configure the `pre-commit` tool to run these checks before commit
by install the git hooks:

```sh
pre-commit install
```

### Managing dependencies

Package dependencies are declared in `pyproject.toml`.

- _package_ dependencies in the `dependencies` array
  in the `[project]` section.
- _development_ dependencies in the `dev` array
  in the `[project.optional-dependencies]` section.

For local development,
the dependencies declared in `pyproject.toml` are pinned to specific versions
using the `requirements.txt` lock file.
You should not manually edit the `requirements.txt` lock file.

#### Adding a new dependency

To install a new Python dependency
add it to the appropriate section in `pyproject.toml`
and then run:

```sh
uv pip compile --output-file=requirements.txt --extra=dev pyproject.toml
```

#### Removing a dependency

Removing Python dependencies works exactly the same way:
edit `pyproject.toml` and then run the `uv pip compile`.

#### Updating all Python packages

Development dependency versions are upgraded automatically
by [Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates)

## Publishing

This package is built and uploaded to PyPI automatically
by the `build_and_publish` workflow
in GitHub Actions.
This workflow will be run whenever a tag is pushed for a new version;
the tag must start with `v`.

To publish a new version of this package:

1. Update the version in `pyproject.toml`.
2. Check all changes have been recorded in [the changelog](./CHANGELOG.md).
3. Add a heading for the new version,
   including today's date.
4. Commit the changes and open a PR.
5. Tag the merge commit with the new version:

   ```sh
   git tag 'v0.0.0'
   git push origin --tags
   ```

The `build_and_publish` workflow will verify
that the tag, package version, and changelog
all contain the same version number.
