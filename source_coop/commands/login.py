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

import getpass
import logging

from source_coop.auth import save_cookies

logger = logging.getLogger("source-coop.commands.login")

def login_command(email=None, password=None, save_path=None):
    """
    Login command implementation

    Args:
        email (str, optional): User's email address (will prompt if None)
        password (str, optional): User's password (will prompt if None)
        save_path (str, optional): Path to save cookies.json (default: ~/.config/source-coop/cookies.json)

    Returns:
        dict: Session cookies if successful, None if failed
    """
    from source_coop.auth import login_to_source_coop

    # Prompt for credentials if not provided
    if email is None:
        email = input("Email: ")
    if password is None:
        password = getpass.getpass("Password: ")

    # Attempt login
    cookies = login_to_source_coop(email, password, save_path)

    if cookies:
        logger.info("Login successful!")
        return cookies
    else:
        logger.error("Login failed.")
        return None
