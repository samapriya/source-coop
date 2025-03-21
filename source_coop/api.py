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
import json
import requests
from pathlib import Path
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger("source-coop.api")

class SourceCoopAPI:
    """API client for Source Coop"""

    BASE_URL = "https://source.coop/api/v1"
    DATA_ENDPOINT = "https://data.source.coop"

    def __init__(self, cookies=None):
        """
        Initialize the API client

        Args:
            cookies (dict, optional): Cookies for authenticated requests
        """
        self.cookies = cookies or {}

    def get_default_headers(self):
        """
        Get default request headers for Source Coop API

        Returns:
            dict: Default headers
        """
        return {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://source.coop/',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }

    def _make_request(self, method, endpoint, **kwargs):
        """
        Make a request to the API

        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            **kwargs: Additional arguments to pass to requests

        Returns:
            dict: Response JSON if successful

        Raises:
            Exception: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self.get_default_headers()

        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                cookies=self.cookies,
                **kwargs
            )

            # Raise exception for 4xx/5xx status codes
            response.raise_for_status()

            if response.status_code in (200, 304):
                return response.json()
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

    def whoami(self):
        """
        Get the currently logged-in user profile information

        Returns:
            dict: User profile data if successful, None otherwise
        """
        try:
            data = self._make_request('GET', 'whoami')
            if data:
                return data.get('account', {}).get('profile', {})
            return None
        except Exception as e:
            logger.error(f"Error making whoami request: {str(e)}")
            return None

    def get_repositories(self, featured=False, limit=10, next_page=None, search=None):
        """
        Get repositories from Source Coop

        Args:
            featured (bool): Whether to list featured repositories
            limit (int): Maximum number of repositories to return
            next_page (str): Token for pagination
            search (str): Search query to filter repositories

        Returns:
            dict: Repository data if successful, None otherwise
        """
        try:
            params = {}
            if not featured and limit:
                params["limit"] = limit
            if not featured and next_page:
                params["next"] = next_page
            if search:
                params["search"] = search

            endpoint = 'repositories/featured' if featured else 'repositories'
            return self._make_request('GET', endpoint, params=params)
        except Exception as e:
            logger.error(f"Error listing repositories: {str(e)}")
            return None

    def get_profile(self, uname):
        """
        Get profile information for a user or organization

        Args:
            uname (str): Username/account ID

        Returns:
            dict: Profile data if successful, None otherwise
        """
        try:
            return self._make_request('GET', f'accounts/{uname}/profile')
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            return None

    def get_members(self, uname):
        """
        Get members of an organization

        Args:
            uname (str): Organization username/account ID

        Returns:
            dict: Members data if successful, None otherwise
        """
        try:
            return self._make_request('GET', f'accounts/{uname}/members')
        except Exception as e:
            logger.error(f"Error getting members: {str(e)}")
            return None
