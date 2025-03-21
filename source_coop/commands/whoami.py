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

from rich.console import Console

logger = logging.getLogger("source-coop.commands.whoami")

def whoami_command():
    """
    Whoami command implementation - Show current user info

    Returns:
        dict: User profile data if successful, None otherwise
    """
    from source_coop.client import SourceCoopClient

    console = Console()
    client = SourceCoopClient()

    if not client.is_authenticated():
        console.print("[yellow]Not logged in. Use 'login' command first.[/yellow]")
        return None

    profile_data = client.api.whoami()

    if profile_data:
        console.print(f"[bold green]Logged in as:[/bold green] {profile_data.get('name', 'Unknown')}")
        return profile_data
    else:
        console.print("[red]Failed to get user profile. You may need to log in again.[/red]")
        return None
