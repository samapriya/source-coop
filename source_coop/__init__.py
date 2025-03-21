"""
Source Coop CLI package - A Python client for Source Coop
"""

import logging

from source_coop.client import SourceCoopClient
from source_coop.api import SourceCoopAPI
from source_coop.s3 import SourceCoopS3
from source_coop.auth import load_cookies, login_to_source_coop, save_cookies

# Set up a null handler for the package's logger
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = '0.1.0'
__author__ = 'Source Coop Team'

__all__ = [
    'SourceCoopClient',
    'SourceCoopAPI',
    'SourceCoopS3',
    'load_cookies',
    'login_to_source_coop',
    'save_cookies',
]
