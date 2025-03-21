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
from rich.table import Table
from rich import box

logger = logging.getLogger("source-coop.commands.summarize")

def display_summary_table(summary):
    """
    Display a table with summary statistics

    Args:
        summary (dict): Summary statistics from list_s3_objects_with_summary
    """
    from source_coop.s3 import SourceCoopS3  # Add this import here

    console = Console()

    # Create the main summary table
    main_table = Table(
        title="Repository Summary",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED
    )

    main_table.add_column("Metric", style="cyan")
    main_table.add_column("Value", style="green")

    main_table.add_row("Total Files", str(summary['total_files']))
    main_table.add_row("Total Size", summary['total_size_human'])

    console.print(main_table)

    # Create the file types table
    if summary['file_types']:
        types_table = Table(
            title="File Types Breakdown",
            show_header=True,
            header_style="bold blue",
            box=box.ROUNDED
        )

        types_table.add_column("Extension", style="cyan")
        types_table.add_column("Count", style="green", justify="right")
        types_table.add_column("Size", style="yellow", justify="right")
        types_table.add_column("Percentage", style="magenta", justify="right")

        # Sort file types by size (descending)
        sorted_types = sorted(
            summary['file_types'].items(),
            key=lambda x: x[1]['size'],
            reverse=True
        )

        for ext, stats in sorted_types:
            percentage = (stats['size'] / summary['total_size'] * 100) if summary['total_size'] > 0 else 0
            types_table.add_row(
                ext,
                str(stats['count']),
                summary['total_size_human'] if ext == 'total' else SourceCoopS3.human_readable_size(stats['size']),
                f"{percentage:.2f}%"
            )

        console.print(types_table)

def display_objects_table(s3_objects, limit=20):
    """
    Display a table with S3 objects

    Args:
        s3_objects (list): List of S3 objects from list_s3_objects_with_summary
        limit (int): Maximum number of objects to display
    """
    from source_coop.s3 import SourceCoopS3  # Add this import here

    console = Console()

    if not s3_objects:
        console.print("[yellow]No objects found[/yellow]")
        return

    # Create the table
    objects_table = Table(
        title=f"Objects (showing {min(limit, len(s3_objects))} of {len(s3_objects)})",
        show_header=True,
        header_style="bold blue",
        box=box.ROUNDED
    )

    objects_table.add_column("Last Modified", style="cyan", no_wrap=True)
    objects_table.add_column("Size", style="green", justify="right")
    objects_table.add_column("Key", style="yellow", overflow="fold")

    # Sort by last modified (newest first)
    sorted_objects = sorted(
        s3_objects,
        key=lambda x: x['last_modified'],
        reverse=True
    )

    # Add rows (limited to specified number)
    for obj in sorted_objects[:limit]:
        objects_table.add_row(
            obj['last_modified'],
            SourceCoopS3.human_readable_size(obj['size']),
            obj['key']
        )

    console.print(objects_table)

def summarize_command(repository, file_type=None):
    """
    Summarize files from a repository

    Args:
        repository (str): Repository URL or S3 URL
        file_type (str, optional): File extension to filter by (e.g. '.csv')
    """
    from source_coop.client import SourceCoopClient
    from source_coop.s3 import SourceCoopS3

    console = Console()
    client = SourceCoopClient()
    s3_client = client.s3

    # Convert repository URL to S3 URL if needed
    if repository.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository)
        if not s3_url:
            console.print("[red]Failed to convert repository URL to S3 URL[/red]")
            return
    else:
        s3_url = repository

    console.print(f"[bold]Using S3 URL:[/bold] {s3_url}")

    # Get objects and summary
    console.print("[bold]Listing objects...[/bold]")
    objects, summary = s3_client.list_objects_with_summary(s3_url, file_type)

    # Display summary
    display_summary_table(summary)

    # Display objects
    display_objects_table(objects)
