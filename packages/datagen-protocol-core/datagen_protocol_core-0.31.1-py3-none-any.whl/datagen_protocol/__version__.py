import sys

if sys.version_info < (3, 10):
    from importlib_metadata import PackageNotFoundError
    from importlib_metadata import version as ver
else:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as ver


def get_version():
    try:
        return ver(__package__ or __name__)
    except PackageNotFoundError:
        return None


sys.modules[__name__] = get_version()  # type: ignore
