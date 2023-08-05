try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # type: ignore[no-redef]


__version__ = version("kolo")
