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
import json
import logging

from rich.console import Console

from .members import display_members_table

logger = logging.getLogger("source-coop.commands.profile")

def profile_command(uname):
    """
    Display profile information for a user or organization

    Args:
        uname (str): Username/account ID

    Returns:
        dict: Profile data if successful, None otherwise
    """
    from source_coop.client import SourceCoopClient

    console = Console()
    client = SourceCoopClient()

    # Get profile data
    profile_data = client.api.get_profile(uname)

    if not profile_data:
        console.print(f"[red]Error: Could not get profile for {uname}[/red]")
        return None

    if profile_data.get('account_type') == 'user':
        # Display user profile
        console.print(f"\n[bold green]User Profile:[/bold green] {uname}")
        console.print(json.dumps(profile_data, indent=2))
    elif profile_data.get('account_type') == 'organization':
        # Display organization profile
        console.print(f"\n[bold green]Organization Profile:[/bold green] {uname}")

        # Show basic org info
        console.print(f"[bold]Name:[/bold] {profile_data.get('name', 'N/A')}")
        console.print(f"[bold]Bio:[/bold] {profile_data.get('bio', 'N/A')}")

        # Get and display members
        console.print("\n[bold]Organization Members:[/bold]")
        members_data = client.api.get_members(uname)
        if members_data:
            display_members_table(members_data)
        else:
            console.print("[yellow]No members data available[/yellow]")

    return profile_data
