# Dev Dependencies

Opinionated development dependencies for python projects.

Install this as your only dev dependency to pick up a bunch of common dev-time libraries you may need for things like linting, type checking and tests.

## Installation

    # Using pipenv:
    pipenv install -d dev-dependencies

## What you get

* Linting

      ruff check .
      black --check .
      # There is also flake8, but ruff is just nicer
      flake8

* Type checking

      mypy devdeps tests

* Tests

      pytest

## Building a package to release

    # Build a distribution (for releases, do this on main with a fresh tag)
    python -m build

    # To release that package
    twine upload dist/dev-dependencies-*.tar.gz dist/dev_dependencies-*-py3-none-any.whl

    # To see what the current version will be
    python -m setuptools_scm


