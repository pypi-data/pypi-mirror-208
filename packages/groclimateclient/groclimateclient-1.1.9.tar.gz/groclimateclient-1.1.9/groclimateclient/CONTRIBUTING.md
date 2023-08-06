# Contributor's Guide

## Install Poetry

We use Poetry to manage packaging for the client library. Using Poetry for
development is encouraged. See [Poetry docs](https://python-poetry.org/docs/)
for full installation instructions.

Here's the tl;dr for OS X and Linux:

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

In case you need to `uninstall` poetry
```sh
curl -sSL https://install.python-poetry.org | python3 - --uninstall
```

You will either need to add poetry to your $PATH or replace all below instances of `poetry` with:
`~/Library/Application\ Support/pypoetry/venv/bin/poetry`

## Get the client library

Clone the repo:

```sh
git clone git@github.com:grointelligence/api-onboarding.git
cd gro-climate-client
```

Install dependencies as well as a local editable copy of the library:

```sh
poetry install
```

**Notes:**
If you want to install from scratch, you can delete `poetry.lock`,
and it will recreate new lock file from `gro-climate-client/pyproject.toml`

Under the hood, Poetry will install a Python virtualenv and fetch the
dependencies.

- `poetry env info` to see where the virtualenv is.
- `poetry env remove <env-name>` to delete the environment. (You can also just
  specify the Python version, eg: `poetry env remove 3.8`)



## Publishing a new release

Our packages on PyPI and TestPyPI:
- https://pypi.org/project/groclimateclient/
- https://test.pypi.org/project/groclimateclient/

**Notes:**
Version will be manually set in `gro-climate-client/pyproject.toml`
Once we have automated release process, we could also integrate [poetry-dynamic-versioning](https://github.com/mtkennerly/poetry-dynamic-versioning)

To build new source and wheel distributions in `dist/`:

```sh
poetry build
```
**Notes:**

Makes sure you double check the compiled version in `dist/`, noticed that sometimes the new version number may not be applied, for reasons like:
- you have installed an old version of groclimateclient in a seaprate project(to fix this, run `pip uninstall groclimateclient`)
- poettry env massed up (unclear why) (to fix this: clean up your virtural env, and try uninstall poetry)

To publish to PyPI, you'll need credentials. Using [PyPI API
tokens](https://pypi.org/help/#apitoken) is recommended, like so:

```sh
poetry publish --username __token__ --password <pypi-token-value-here>
```

You can find pypi-token in shared [Gro Ops Passwords](https://docs.google.com/spreadsheets/d/19G8u229adwani2TR9iJ7CQ60EOftlW4EzziFy5fOyGc/edit#gid=0)

You can also publish with the username and password for the [gro-intelligence
account on PyPA](https://pypi.org/user/gro-intelligence/) (found in [Gro Ops Passwords](https://docs.google.com/spreadsheets/d/19G8u229adwani2TR9iJ7CQ60EOftlW4EzziFy5fOyGc/edit#gid=0)).

### Publishing to TestPyPI

You'll need to first configure the repository:

- configure the repository (only need to do this once): `poetry config
  repositories.testpypi https://test.pypi.org/legacy/`
- or, use an environment variable: `export
  POETRY_REPOSITORIES_TESTPYPI_URL=https://test.pypi.org/legacy/`

Then add `-r testpypi` to the publish command:

```sh
poetry publish -r testpypi --username __token__ --password <pypi-token-value-here>
```
Similarly, pypi-token can be found in [Gro Ops Passwords](https://docs.google.com/spreadsheets/d/19G8u229adwani2TR9iJ7CQ60EOftlW4EzziFy5fOyGc/edit#gid=0):

### Conda package details

Not supported yet
