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

from rich import box
from rich.console import Console
from rich.table import Table

logger = logging.getLogger("source-coop.commands.members")

def display_members_table(members_data):
    """
    Display organization members in a nicely formatted table

    Args:
        members_data (list): List of member dictionaries
    """
    if not members_data:
        logger.info("No members data available")
        return

    # Create a rich table
    console = Console()
    table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)

    # Add columns based on the data structure
    table.add_column("Membership ID", style="cyan")
    table.add_column("Account ID", style="green")
    table.add_column("Role", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("Membership Account ID", style="blue")
    table.add_column("State Changed", style="bright_cyan")

    # Add rows - using the correct structure
    for member in members_data:
        table.add_row(
            member.get('membership_id', 'N/A'),
            member.get('account_id', 'N/A'),
            member.get('role', 'N/A'),
            member.get('state', 'N/A'),
            member.get('membership_account_id', 'N/A'),
            member.get('state_changed', 'N/A')
        )

    # Print the table
    console.print(table)

def members_command(organization):
    """
    Get members of an organization

    Args:
        organization (str): Organization username/account ID

    Returns:
        list: Members data if successful, None otherwise
    """
    from source_coop.client import SourceCoopClient

    console = Console()
    client = SourceCoopClient()

    # Get members data
    members_data = client.api.get_members(organization)

    if members_data:
        display_members_table(members_data)
        return members_data
    else:
        console.print(f"[red]Error: Could not get members for organization {organization}[/red]")
        return None
