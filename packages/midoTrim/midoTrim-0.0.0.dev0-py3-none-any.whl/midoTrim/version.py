import packaging.version

try:
    # Python 3.8+
    import importlib.metadata as importlib_metadata
except ImportError:
    # <Python 3.7 and lower
    import importlib_metadata

__version__ = "0.0.0.dev0"

try:
    __version__ = importlib_metadata.version("midoTrim")
except importlib_metadata.PackageNotFoundError:
    # package is not installed
    pass

version_info = packaging.version.Version(__version__)
