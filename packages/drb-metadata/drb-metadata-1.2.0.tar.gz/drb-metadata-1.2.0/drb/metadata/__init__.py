from .metadata import DrbMetadata, DrbMetadataResolver
from . import _version

__all__ = [
    'DrbMetadata',
    'DrbMetadataResolver',
]
__version__ = _version.get_versions()['version']
