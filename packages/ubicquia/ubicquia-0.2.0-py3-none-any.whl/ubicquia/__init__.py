"""Ubicquia Python API Client Package

This package provides a Python API Client for the Ubicquia.

API Documentation
=================

    https://swagger.ubicquia.com/#/pages/swagger
"""

from .base import TokenUpdate, UbicquiaSession
from .client import Ubicquia

__version__ = '0.2.0'

__all__ = [
    '__version__',

    'UbicquiaSession',
    'Ubicquia',
    'TokenUpdate'
]
