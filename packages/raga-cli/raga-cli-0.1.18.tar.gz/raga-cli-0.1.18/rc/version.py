# pylint: disable=unused-import
try:
    from ._rc_version import version as __version__
    from ._rc_version import version_tuple
except ImportError:
    __version__ = "UNKNOWN"
    version_tuple = (0, 0, __version__)  # type: ignore[assignment]
