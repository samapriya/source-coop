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

import csv
import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from rich import box
from rich.console import Console
from rich.table import Table

logger = logging.getLogger("source-coop.commands.repos")

def display_repositories(data):
    """
    Display repository information in a nicely formatted table

    Args:
        data (dict): Repository data from the API
    """
    console = Console()

    # Create the table with improved layout for internationalization
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
        collapse_padding=False,
        pad_edge=True,
        expand=True,
        width=None,  # Let Rich determine optimal width
        safe_box=True  # Better handling of Unicode characters
    )

    # Add columns with width constraints
    table.add_column("Repository ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="green", overflow="fold")  # Will fold text properly
    table.add_column("Account", style="blue", no_wrap=True)
    table.add_column("Tags", style="yellow", overflow="fold")
    table.add_column("Published", style="magenta", no_wrap=True, width=26)  # Fixed width for dates
    table.add_column("Data Mode", style="red", no_wrap=True, width=10)
    table.add_column("Featured", style="bright_cyan", no_wrap=True, width=8)

    # Add rows
    for repo in data.get('repositories', []):
        # Get the values, providing defaults if not present
        repo_id = repo.get('repository_id', 'N/A')
        title = repo.get('meta', {}).get('title', 'N/A')
        account_id = repo.get('account_id', 'N/A')

        # Handle tags better - limit to first 3 and add ellipsis if more
        tags_list = repo.get('meta', {}).get('tags', [])
        if len(tags_list) > 3:
            tags = ", ".join(tags_list[:3]) + "..."
        else:
            tags = ", ".join(tags_list)

        published = repo.get('published', 'N/A')
        data_mode = repo.get('data_mode', 'N/A')
        featured = "Yes" if repo.get('featured') else "No"

        table.add_row(repo_id, title, account_id, tags, published, data_mode, featured)

    # Print additional information
    console.print(f"\n[bold]Total count:[/bold] {data.get('count', 'N/A')}")
    if 'next' in data:
        console.print(f"[bold]Next page:[/bold] {data.get('next')}")

    # Print the table with a specific width that can accommodate CJK characters
    console.print(table)

def export_repositories(data, export_format='json', output_path=None):
    """
    Export repository data to CSV, Parquet, or JSON format

    Args:
        data (dict): Repository data from the API
        export_format (str): Format to export data to ('csv', 'parquet', or 'json')
        output_path (str, optional): Custom output path for the exported file

    Returns:
        str: Path to the exported file if successful, None otherwise
    """
    if not data or 'repositories' not in data or not data['repositories']:
        logger.error("No repository data to export")
        return None

    # Create output directory if needed
    export_dir = Path('exports')
    export_dir.mkdir(exist_ok=True)

    # Generate default filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    featured_str = "featured-" if any(repo.get('featured') for repo in data['repositories']) else ""
    default_filename = f"source-coop-{featured_str}repositories-{timestamp}"

    # Use provided output path or generate default path
    if output_path:
        file_path = Path(output_path)
        # If output_path is a directory, use default filename
        if file_path.is_dir():
            file_path = file_path / default_filename
    else:
        file_path = export_dir / default_filename

    # Normalize repository data to flatten structure for export
    repositories = []
    for repo in data['repositories']:
        flat_repo = {
            'repository_id': repo.get('repository_id'),
            'account_id': repo.get('account_id'),
            'title': repo.get('meta', {}).get('title'),
            'description': repo.get('meta', {}).get('description'),
            'tags': ','.join(repo.get('meta', {}).get('tags', [])),
            'published': repo.get('published'),
            'updated': repo.get('updated'),
            'data_mode': repo.get('data_mode'),
            'featured': 'Yes' if repo.get('featured') else 'No'
        }
        repositories.append(flat_repo)

    try:
        if export_format.lower() == 'json':
            # Export to JSON
            file_path = file_path.with_suffix('.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'repositories': repositories,
                    'count': len(repositories),
                    'exported_at': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)

        elif export_format.lower() == 'csv':
            # Export to CSV
            file_path = file_path.with_suffix('.csv')
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                if repositories:
                    writer = csv.DictWriter(f, fieldnames=repositories[0].keys())
                    writer.writeheader()
                    writer.writerows(repositories)

        elif export_format.lower() == 'parquet':
            # Export to Parquet (requires pandas and pyarrow)
            file_path = file_path.with_suffix('.parquet')
            df = pd.DataFrame(repositories)
            df.to_parquet(file_path, index=False)

        else:
            logger.error(f"Unsupported export format: {export_format}")
            return None

        logger.info(f"Successfully exported repositories to {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"Error exporting repositories: {e}")
        return None

def repos_command(featured=False, limit=10, next_page=None, search=None, display=True, export_format=None, output_path=None):
    """
    List repositories command implementation

    Args:
        featured (bool): Whether to list featured repositories
        limit (int): Maximum number of repositories to return
        next_page (str): Token for pagination
        search (str): Search query to filter repositories
        display (bool): Whether to display the repositories in a table
        export_format (str, optional): Format to export data ('csv', 'parquet', or 'json')
        output_path (str, optional): Custom output path for the exported file

    Returns:
        dict: Repository data if successful, None otherwise
    """
    from source_coop.client import SourceCoopClient

    console = Console()
    client = SourceCoopClient()

    # Get repositories from API
    data = client.api.get_repositories(featured, limit, next_page, search)

    if not data:
        console.print("[red]Error fetching repositories.[/red]")
        return None

    # Display the repositories in a table if requested
    if display and data:
        display_repositories(data)

    # Export data if export_format is specified
    if export_format and data:
        export_path = export_repositories(data, export_format, output_path)
        if export_path:
            console.print(f"[bold green]Exported data to:[/bold green] {export_path}")

    return data
