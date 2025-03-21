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


import asyncio
import logging
import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn
)
import aiohttp
import aiofiles
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

logger = logging.getLogger("source-coop.commands.download")

async def download_s3_objects_async(s3_objects, output_dir, max_concurrent=10, multipart_count=8, quiet=False):
    """
    Download S3 objects to a local directory using asynchronous requests with multipart support

    Args:
        s3_objects (list): List of S3 objects from list_s3_objects_with_summary
        output_dir (str): Directory to save downloaded files
        max_concurrent (int): Maximum number of concurrent downloads
        multipart_count (int): Number of parts to split large file downloads into
        quiet (bool): If True, don't ask for confirmation

    Returns:
        int: Number of successfully downloaded files
    """
    from source_coop.s3 import SourceCoopS3

    console = Console()

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Count files to download
    total_files = len(s3_objects)
    if total_files == 0:
        console.print("[yellow]No files to download[/yellow]")
        return 0

    # Confirm download if not in quiet mode
    total_size = sum(obj['size'] for obj in s3_objects)
    download_prompt = f"Download {total_files} files ({SourceCoopS3.human_readable_size(total_size)}) to {output_dir}?"

    if not quiet and not Confirm.ask(download_prompt):
        console.print("Download cancelled")
        return 0

    # Show appropriate message based on multipart_count
    if multipart_count > 1:
        console.print(f"[bold green]Downloading {total_files} files to {output_dir} using up to {max_concurrent} concurrent connections and {multipart_count} parts for large files...[/bold green]")
    else:
        console.print(f"[bold green]Downloading {total_files} files to {output_dir} using up to {max_concurrent} concurrent connections...[/bold green]")

    # Sort objects by size (download larger files first)
    sorted_objects = sorted(s3_objects, key=lambda x: x['size'], reverse=True)

    # Track successful downloads
    successful = 0
    failed = 0

    # Semaphore to limit concurrent downloads
    semaphore = asyncio.Semaphore(max_concurrent)

    # Setup progress display - using standard context manager (not async)
    progress = Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(bar_width=50),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
        console=console,
        expand=True
    )

    # Threshold for multipart downloads (files larger than 10MB)
    MULTIPART_THRESHOLD = 10 * 1024 * 1024

    # Simplified multipart download approach
    async def download_file_multipart(obj, task_id):
        file_key = obj['key']
        file_url = obj['download_url']
        file_size = obj['size']

        # Create output path (preserve directory structure)
        rel_path = file_key
        out_file = output_path / rel_path

        # Create parent directories if needed
        out_file.parent.mkdir(parents=True, exist_ok=True)

        # Try first with a HEAD request to check if the server supports Range
        supports_range = False
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(file_url, timeout=30) as response:
                    # Check if server supports range requests
                    supports_range = "accept-ranges" in response.headers and response.headers["accept-ranges"] == "bytes"
        except Exception:
            # If HEAD fails, assume no range support
            supports_range = False

        # If server doesn't support range or we're forcing a single part download
        if not supports_range or multipart_count <= 1:
            # Fallback to regular download
            return await download_file_single(obj, task_id)

        # Calculate part boundaries
        part_size = file_size // multipart_count
        parts = []
        for i in range(multipart_count):
            start_byte = i * part_size
            # Make sure the last part includes any remaining bytes
            end_byte = file_size - 1 if i == multipart_count - 1 else (i + 1) * part_size - 1
            parts.append((start_byte, end_byte, i))

        # Create temporary part files
        part_files = []
        for _, _, i in parts:
            part_file = output_path / f"{rel_path}.part{i}"
            part_files.append(part_file)

        # Download each part
        async def download_part(start_byte, end_byte, part_num):
            part_file = part_files[part_num]

            headers = {'Range': f'bytes={start_byte}-{end_byte}'}

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_url, headers=headers, timeout=60) as response:
                        if response.status == 206:  # Partial Content
                            # Create directory for part file if needed
                            part_file.parent.mkdir(parents=True, exist_ok=True)

                            # Write the part to a file
                            async with aiofiles.open(part_file, 'wb') as f:
                                downloaded = 0
                                async for chunk in response.content.iter_chunked(64 * 1024):  # 64KB chunks
                                    await f.write(chunk)
                                    downloaded += len(chunk)
                                    progress.update(task_id, advance=len(chunk))

                            return True
                        else:
                            # Non-206 response means range request failed
                            if not quiet:
                                console.print(f"[yellow]Range request failed for part {part_num} with status {response.status}, falling back to single download[/yellow]")
                            return False
            except Exception as e:
                if not quiet:
                    console.print(f"[red]Error downloading part {part_num}: {str(e)}[/red]")
                return False

        # Start downloading all parts
        part_results = await asyncio.gather(*[download_part(start, end, i) for start, end, i in parts])

        # Check if all parts downloaded successfully
        if all(part_results):
            try:
                # Combine all parts into the final file
                async with aiofiles.open(out_file, 'wb') as outfile:
                    for part_file in part_files:
                        if part_file.exists():
                            async with aiofiles.open(part_file, 'rb') as infile:
                                await outfile.write(await infile.read())

                # Clean up part files
                for part_file in part_files:
                    try:
                        if part_file.exists():
                            part_file.unlink()
                    except:
                        pass

                return True
            except Exception as e:
                if not quiet:
                    console.print(f"[red]Error combining parts: {str(e)}[/red]")
                return False
        else:
            # If any part failed, fall back to single download
            if not quiet:
                console.print(f"[yellow]Some parts failed, falling back to single download for {file_key}[/yellow]")

            # Clean up any part files
            for part_file in part_files:
                try:
                    if part_file.exists():
                        part_file.unlink()
                except:
                    pass

            # Reset progress
            progress.update(task_id, completed=0)

            # Fall back to single download
            return await download_file_single(obj, task_id)

    # Standard single download
    async def download_file_single(obj, task_id):
        file_key = obj['key']
        file_url = obj['download_url']
        file_size = obj['size']

        # Create output path (preserve directory structure)
        rel_path = file_key
        out_file = output_path / rel_path

        # Create parent directories if needed
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Start download with increased timeout
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url, timeout=300) as response:  # 5 minute timeout
                    if response.status == 200:
                        # Open file for writing
                        async with aiofiles.open(out_file, 'wb') as f:
                            # Process the response body in chunks
                            chunk_size = 128 * 1024  # 128KB chunks (larger for better performance)
                            downloaded = 0

                            async for chunk in response.content.iter_chunked(chunk_size):
                                await f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task_id, completed=downloaded)

                        return True
                    else:
                        if not quiet:
                            console.print(f"[red]Failed to download {file_key}: HTTP {response.status}[/red]")
                        return False

        except Exception as e:
            if not quiet:
                console.print(f"[red]Error downloading {file_key}: {str(e)}[/red]")
            return False

    # Main download coroutine - decide which method to use
    async def download_file(obj):
        nonlocal successful, failed

        file_key = obj['key']
        file_size = obj['size']

        # Use the semaphore to limit concurrent downloads
        async with semaphore:
            try:
                # Create a progress bar for this file
                task_id = progress.add_task(f"[cyan]{os.path.basename(file_key)}", total=file_size)

                # Choose download method based on file size
                # Only use multipart for larger files where it makes sense
                use_multipart = multipart_count > 1 and file_size > MULTIPART_THRESHOLD

                if use_multipart:
                    result = await download_file_multipart(obj, task_id)
                else:
                    result = await download_file_single(obj, task_id)

                if result:
                    successful += 1
                else:
                    failed += 1
                    try:
                        progress.update(task_id, visible=False)
                    except:
                        pass

            except Exception as e:
                if not quiet:
                    console.print(f"[red]Error downloading {file_key}: {str(e)}[/red]")
                failed += 1

    # Create a list to hold the download tasks
    download_tasks = []

    # Start the progress display
    with progress:
        # Create a task for each object
        for obj in sorted_objects:
            download_tasks.append(download_file(obj))

        # Run all downloads concurrently
        await asyncio.gather(*download_tasks)

    # Final summary
    console.print(f"[bold green]Successfully downloaded {successful} of {total_files} files[/bold green]")
    if failed > 0:
        console.print(f"[bold red]Failed to download {failed} files[/bold red]")

    return successful

def download_s3_objects_sync(s3_objects, output_dir, quiet=False):
    """
    Fallback synchronous version for downloading S3 objects using ThreadPoolExecutor

    Args:
        s3_objects (list): List of S3 objects from list_s3_objects_with_summary
        output_dir (str): Directory to save downloaded files
        quiet (bool): If True, don't ask for confirmation

    Returns:
        int: Number of successfully downloaded files
    """
    from source_coop.s3 import SourceCoopS3

    console = Console()

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Count files to download
    total_files = len(s3_objects)
    if total_files == 0:
        console.print("[yellow]No files to download[/yellow]")
        return 0

    # Confirm download if not in quiet mode
    total_size = sum(obj['size'] for obj in s3_objects)
    download_prompt = f"Download {total_files} files ({SourceCoopS3.human_readable_size(total_size)}) to {output_dir}?"

    if not quiet and not Confirm.ask(download_prompt):
        console.print("Download cancelled")
        return 0

    console.print(f"[bold yellow]Using synchronous download fallback with ThreadPoolExecutor[/bold yellow]")
    console.print(f"[bold green]Downloading {total_files} files to {output_dir}...[/bold green]")

    # Sort objects by size (download larger files first)
    sorted_objects = sorted(s3_objects, key=lambda x: x['size'], reverse=True)

    # Track successful downloads
    successful = 0
    failed = 0

    # Define the download function
    def download_file(obj):
        nonlocal successful, failed

        file_key = obj['key']
        file_url = obj['download_url']
        file_size = obj['size']

        # Create output path (preserve directory structure)
        rel_path = file_key
        out_file = output_path / rel_path

        # Create parent directories if needed
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Download with progress bar for larger files
            with requests.get(file_url, stream=True, timeout=300) as response:  # Increased timeout
                if response.status_code == 200:
                    if not quiet and file_size > 1024*10:  # Show progress bar for files > 10KB
                        with tqdm(
                            total=file_size,
                            unit='B',
                            unit_scale=True,
                            unit_divisor=1024,
                            desc=os.path.basename(file_key),
                            ncols=100
                        ) as progress_bar:
                            with open(out_file, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=128*1024):  # Larger chunks
                                    if chunk:
                                        f.write(chunk)
                                        progress_bar.update(len(chunk))
                    else:
                        with open(out_file, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=128*1024):
                                if chunk:
                                    f.write(chunk)

                    successful += 1
                    return True
                else:
                    if not quiet:
                        console.print(f"[red]Failed to download {file_key}: HTTP {response.status_code}[/red]")
                    failed += 1
                    return False
        except Exception as e:
            if not quiet:
                console.print(f"[red]Error downloading {file_key}: {str(e)}[/red]")
            failed += 1
            return False

    # Use ThreadPoolExecutor for concurrent downloads
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_file, sorted_objects))

    # Final summary
    console.print(f"[bold green]Successfully downloaded {successful} of {total_files} files[/bold green]")
    if failed > 0:
        console.print(f"[bold red]Failed to download {failed} files[/bold red]")

    return successful

def download_s3_objects(s3_objects, output_dir, multipart_count=8, max_concurrent=10, quiet=False):
    """
    Download S3 objects to a local directory (wrapper for async function)

    Args:
        s3_objects (list): List of S3 objects from list_s3_objects_with_summary
        output_dir (str): Directory to save downloaded files
        multipart_count (int): Number of parts to split large file downloads into
        max_concurrent (int): Maximum number of concurrent downloads
        quiet (bool): If True, don't ask for confirmation

    Returns:
        int: Number of successfully downloaded files
    """
    try:
        # Use asyncio.run() which creates a new event loop and closes it afterwards
        return asyncio.run(download_s3_objects_async(
            s3_objects,
            output_dir,
            max_concurrent=max_concurrent,
            multipart_count=multipart_count,
            quiet=quiet
        ))
    except RuntimeError as e:
        # Handle the case where we're in an environment that already has an event loop
        if "This event loop is already running" in str(e):
            logger.warning("Detected running event loop, falling back to synchronous downloads")
            return download_s3_objects_sync(s3_objects, output_dir, quiet)
        else:
            logger.error(f"Runtime error during download: {str(e)}")
            return 0
    except Exception as e:
        logger.error(f"Error during download: {str(e)}")
        return 0

def download_command(repository, file_type=None, output_dir=None, threads=10, multipart=8, quiet=False):
    """
    Download files from a repository

    Args:
        repository (str): Repository URL or S3 URL
        file_type (str, optional): File extension to filter by (e.g. '.csv')
        output_dir (str, optional): Directory to save downloaded files
        threads (int): Number of concurrent download threads
        multipart (int): Number of parts to split large file downloads into (0 to disable)
        quiet (bool): If True, don't ask for confirmation and don't display object list
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

    # Set default output directory if not provided
    if not output_dir:
        # Extract repository name from S3 URL
        _, prefix = SourceCoopS3.parse_s3_url(s3_url)
        repo_name = prefix.strip('/').split('/')[-1] if prefix else "download"
        output_dir = f"./source-coop-{repo_name}"
        console.print(f"[bold]Using default output directory:[/bold] {output_dir}")

    # Get objects and summary
    console.print("[bold]Listing objects...[/bold]")
    objects, summary = s3_client.list_objects_with_summary(s3_url, file_type)

    # Display summary if not quiet
    if not quiet:
        from .summarize import display_summary_table, display_objects_table
        display_summary_table(summary)
        display_objects_table(objects)

    # Download the files
    if objects:
        download_s3_objects(objects, output_dir, multipart_count=multipart, max_concurrent=threads, quiet=quiet)
    else:
        console.print("[yellow]No files found to download[/yellow]")
