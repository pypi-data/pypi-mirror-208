from importlib.metadata import PackageNotFoundError, version

import toml

VERSION: str | None = None
__version__: str | None = None
try:
    VERSION = version(__package__)
    __version__ = version(__package__)
except PackageNotFoundError:  # pragma: no cover
    # package is not installed?
    __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"] + "dev"
