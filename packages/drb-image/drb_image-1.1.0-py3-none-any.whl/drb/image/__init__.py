from . import _version
from .image import (Image, AddonImage)

__version__ = _version.get_versions()['version']

__all__ = [
    'Image',
    'AddonImage'
]
