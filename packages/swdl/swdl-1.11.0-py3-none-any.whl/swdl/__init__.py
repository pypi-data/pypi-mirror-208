from . import _version
from .config import Settings

settings = Settings()

__version__ = _version.get_versions()["version"]
