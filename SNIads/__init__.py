from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("SNIads")
except PackageNotFoundError:
    __version__ = "unknown"
