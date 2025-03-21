"""
Copyright 2025 Samapriya Roy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Source Coop download command implementation
"""

import logging

from source_coop.api import SourceCoopAPI
from source_coop.auth import load_cookies
from source_coop.s3 import SourceCoopS3

logger = logging.getLogger("source-coop.client")

class SourceCoopClient:
    """Main client for Source Coop integrating API and S3 functionality"""

    def __init__(self, cookies=None):
        """
        Initialize the Source Coop client

        Args:
            cookies (dict, optional): Cookies for authenticated requests
                                     If None, will attempt to load from default location
        """
        # Load cookies from default location if not provided
        self.cookies = cookies or load_cookies()

        # Initialize API client with cookies
        self.api = SourceCoopAPI(self.cookies)

        # Initialize S3 client
        self.s3 = SourceCoopS3()

    def is_authenticated(self):
        """
        Check if the client has authentication cookies

        Returns:
            bool: True if client has authentication cookies, False otherwise
        """
        # Check if we have both csrf_token and ory_session cookies
        has_csrf = any("csrf_token" in key for key in self.cookies.keys())
        has_session = any("ory_session" in key for key in self.cookies.keys())

        return has_csrf and has_session
