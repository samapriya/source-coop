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
import json
import logging
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

logger = logging.getLogger("source-coop.auth")

def get_cookie_path():
    """
    Get the default path for cookies.json

    Returns:
        Path: Path object for the cookies.json file
    """
    config_dir = Path.home() / ".config" / "source-coop"
    return config_dir / "cookies.json"

def load_cookies():
    """
    Load cookies from the default path if it exists
    Filters to only include important cookies (csrf_token and ory_session)

    Returns:
        dict: Important cookie dictionary if file exists, empty dict otherwise
    """
    cookie_path = get_cookie_path()

    if not cookie_path.exists():
        logger.info(f"Cookie file not found at {cookie_path}")
        return {}

    try:
        with open(cookie_path, 'r') as f:
            all_cookies = json.load(f)

        # Get the important cookies (csrf token and session)
        important_cookies = {}
        count = 0

        for key, value in all_cookies.items():
            if "csrf_token" in key or "ory_session" in key:
                important_cookies[key] = value
                count += 1

            if count >= 2:
                break

        logger.debug(f"Loaded {count} important cookies")
        return important_cookies
    except Exception as e:
        logger.error(f"Error reading cookie file: {str(e)}")
        return {}

def save_cookies(cookies, save_path=None):
    """
    Save cookies to a file

    Args:
        cookies (dict): Cookies to save
        save_path (Path, optional): Path to save cookies.json (default: ~/.config/source-coop/cookies.json)

    Returns:
        bool: True if saved successfully, False otherwise
    """
    if save_path is None:
        save_path = get_cookie_path()

    # Ensure directory exists
    save_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(save_path, 'w') as f:
            json.dump(cookies, f, indent=2)
        logger.info(f"Cookies saved to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving cookies: {str(e)}")
        return False

def login_to_source_coop(email=None, password=None, save_path=None):
    """
    Log in to source.coop and save cookies to file

    Args:
        email: User's email address (will prompt if None)
        password: User's password (will prompt if None)
        save_path: Path to save cookies.json (overwrites existing file)
                  If None, saves to ~/.config/source-coop/cookies.json

    Returns:
        dict: Session cookies if successful, None if failed
    """
    # Set default path in user's config directory if not specified
    if save_path is None:
        config_dir = Path.home() / ".config" / "source-coop"
        config_dir.mkdir(parents=True, exist_ok=True)
        save_path = config_dir / "cookies.json"

    # Prompt for credentials if not provided
    if email is None:
        email = input("Email: ")
    if password is None:
        password = getpass.getpass("Password: ")

    # Base URL and session setup
    base_url = "https://auth.source.coop"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })

    try:
        response = session.get(f"{base_url}/self-service/login/browser")
        redirect_url = response.url
        parsed_url = urlparse(redirect_url)
        flow_id = parse_qs(parsed_url.query).get('flow', [None])[0]

        if not flow_id:
            logger.error("Failed to get login flow ID")
            return None

        login_flow_url = f"{base_url}/self-service/login/flows?id={flow_id}"
        flow_response = session.get(login_flow_url)

        if flow_response.status_code != 200:
            logger.error(f"Failed to get login flow: {flow_response.status_code}")
            return None

        flow_data = flow_response.json()

        csrf_token = None
        for node in flow_data.get("ui", {}).get("nodes", []):
            if node.get("attributes", {}).get("name") == "csrf_token":
                csrf_token = node.get("attributes", {}).get("value")
                break

        if not csrf_token:
            logger.error("CSRF token not found in login flow")
            return None

        login_data = {
            "csrf_token": csrf_token,
            "method": "password",
        }

        for node in flow_data.get("ui", {}).get("nodes", []):
            name = node.get("attributes", {}).get("name", "")
            if name in ["identifier", "username", "email"]:
                login_data[name] = email
            elif name == "password":
                login_data[name] = password

        login_url = f"{base_url}/self-service/login?flow={flow_id}"
        response = session.post(
            login_url,
            data=login_data,
            allow_redirects=True
        )

        cookies = session.cookies.get_dict()
        session_cookie = next((cookie for cookie in cookies if "ory_session" in cookie), None)

        if not session_cookie:
            logger.error("Login failed, no session cookie found")
            return None

        # Save cookies
        save_cookies(cookies, save_path)

        logger.info(f"Login successful! Cookies saved to {save_path}")
        return cookies

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return None
