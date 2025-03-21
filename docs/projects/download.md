# Downloading Repository Contents

The `download` command allows you to download files from Source Coop repositories efficiently. It supports concurrent downloads, multipart transfers for large files, and filtering by file type.

## CLI Usage

To download all files from a repository:

```bash
source-coop download REPOSITORY_URL
```

You can use either a web URL (https://source.coop/account/repository) or an S3 URL (s3://account/repository).

### Filtering by File Type

You can filter to download only files of a specific type:

```bash
source-coop download REPOSITORY_URL --file-type .tif
```

This will only download files with the specified extension (e.g., `.tif`, `.csv`, `.json`).

### Specifying Output Directory

By default, files are downloaded to a directory named `./source-coop-<repository_name>`. You can specify a custom output directory:

```bash
source-coop download REPOSITORY_URL --output-dir ./my-data-directory
```

### Controlling Concurrency

You can adjust the number of concurrent downloads to optimize for your connection:

```bash
source-coop download REPOSITORY_URL --threads 20
```

This will download up to 20 files simultaneously (default is 10).

### Multipart Downloads

For large files, the download command uses multipart transfers by default. You can adjust the number of parts or disable this feature:

```bash
# Use 16 parts for large files
source-coop download REPOSITORY_URL --multipart 16

# Disable multipart downloading
source-coop download REPOSITORY_URL --multipart 0
```

### Quiet Mode

For automated scripts or when you don't need to see detailed output:

```bash
source-coop download REPOSITORY_URL --quiet
```

This skips confirmation prompts and detailed file listings.

### Example Output

```
Using S3 URL: s3://example-org/landsat-dataset

Listing objects...

Repository Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric     │ Value         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Total Files│ 156           │
│ Total Size │ 2.34 GB       │
└────────────┴───────────────┘

[... file listings ...]

Download 156 files (2.34 GB) to ./source-coop-landsat-dataset? [y/n]: y

Downloading 156 files to ./source-coop-landsat-dataset using up to 10 concurrent connections and 8 parts for large files...

[file1.tif] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% • 25.6 MB • 5.4 MB/s • 0:00:04
[file2.tif] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% • 25.3 MB • 5.2 MB/s • 0:00:04
[file3.tif] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% • 24.9 MB • 6.1 MB/s • 0:00:04
[...]

Successfully downloaded 156 of 156 files
```

### CLI Help

For more options and help:

```bash
source-coop download --help
```

## Python SDK Usage

### Basic Download

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
from source_coop.commands.download import download_s3_objects

def download_repository(repository_url, output_dir=None, file_type=None):
    # Create a client instance
    client = SourceCoopClient()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            print("Failed to convert repository URL to S3 URL.")
            return False
    else:
        s3_url = repository_url
    
    print(f"Using S3 URL: {s3_url}")
    
    # Set default output directory if not provided
    if not output_dir:
        # Extract repository name from S3 URL
        _, prefix = SourceCoopS3.parse_s3_url(s3_url)
        repo_name = prefix.strip('/').split('/')[-1] if prefix else "download"
        output_dir = f"./source-coop-{repo_name}"
    
    print(f"Using output directory: {output_dir}")
    
    # Get objects to download
    print("Listing objects...")
    objects, summary = client.s3.list_objects_with_summary(s3_url, file_type=file_type)
    
    if not objects:
        print("No objects found to download.")
        return False
    
    # Display summary
    print(f"\nFound {summary['total_files']} files ({summary['total_size_human']})")
    
    # Download the files
    successful = download_s3_objects(
        objects,
        output_dir,
        max_concurrent=10,
        multipart_count=8,
        quiet=False
    )
    
    print(f"\nDownload complete. {successful} files downloaded successfully.")
    return successful > 0

if __name__ == "__main__":
    download_repository("https://source.coop/example-org/landsat-dataset")
```

### Customized Download with Options

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
from source_coop.commands.download import download_s3_objects
from pathlib import Path

def download_with_options(
    repository_url,
    output_dir=None,
    file_type=None,
    max_concurrent=10,
    multipart_count=8,
    quiet=False
):
    client = SourceCoopClient()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            print("Failed to convert repository URL to S3 URL.")
            return False
    else:
        s3_url = repository_url
    
    print(f"Using S3 URL: {s3_url}")
    
    # Set default output directory if not provided
    if not output_dir:
        # Extract repository name from S3 URL
        _, prefix = SourceCoopS3.parse_s3_url(s3_url)
        repo_name = prefix.strip('/').split('/')[-1] if prefix else "download"
        output_dir = f"./source-coop-{repo_name}"
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Using output directory: {output_dir}")
    print(f"Concurrent downloads: {max_concurrent}")
    print(f"Multipart count: {multipart_count}")
    
    # Get objects and summary
    if not quiet:
        print("Listing objects...")
    
    objects, summary = client.s3.list_objects_with_summary(s3_url, file_type=file_type)
    
    if not objects:
        print("No objects found to download.")
        return False
    
    # Display summary if not in quiet mode
    if not quiet:
        print(f"\nFound {summary['total_files']} files ({summary['total_size_human']})")
        
        # Show file type breakdown
        print("\nFile Types:")
        for ext, stats in sorted(summary['file_types'].items(), key=lambda x: x[1]['size'], reverse=True):
            percentage = (stats['size'] / summary['total_size'] * 100) if summary['total_size'] > 0 else 0
            print(f"- {ext}: {stats['count']} files, {SourceCoopS3.human_readable_size(stats['size'])} ({percentage:.2f}%)")
    
    # Download the files
    successful = download_s3_objects(
        objects,
        output_dir,
        max_concurrent=max_concurrent,
        multipart_count=multipart_count,
        quiet=quiet
    )
    
    if not quiet:
        print(f"\nDownload complete. {successful} of {len(objects)} files downloaded successfully.")
    
    return successful

if __name__ == "__main__":
    download_with_options(
        "https://source.coop/example-org/landsat-dataset",
        output_dir="./data",
        file_type=".tif",
        max_concurrent=20,
        multipart_count=16,
        quiet=False
    )
```

### Downloading Specific Files

If you want to download only specific files rather than everything in a repository:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
from source_coop.commands.download import download_s3_objects
from pathlib import Path

def download_specific_files(repository_url, key_patterns, output_dir=None):
    client = SourceCoopClient()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            print("Failed to convert repository URL to S3 URL.")
            return False
    else:
        s3_url = repository_url
    
    # Set default output directory if not provided
    if not output_dir:
        # Extract repository name from S3 URL
        _, prefix = SourceCoopS3.parse_s3_url(s3_url)
        repo_name = prefix.strip('/').split('/')[-1] if prefix else "download"
        output_dir = f"./source-coop-{repo_name}"
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Using S3 URL: {s3_url}")
    print(f"Using output directory: {output_dir}")
    
    # Get all objects in the repository
    print("Listing objects...")
    objects, _ = client.s3.list_objects_with_summary(s3_url)
    
    if not objects:
        print("No objects found in the repository.")
        return False
    
    # Filter objects based on patterns
    filtered_objects = []
    for obj in objects:
        key = obj['key']
        if any(pattern in key for pattern in key_patterns):
            filtered_objects.append(obj)
    
    if not filtered_objects:
        print("No objects matched the specified patterns.")
        return False
    
    # Calculate total size
    total_size = sum(obj['size'] for obj in filtered_objects)
    total_size_human = SourceCoopS3.human_readable_size(total_size)
    
    print(f"Found {len(filtered_objects)} matching files ({total_size_human})")
    
    # Download the filtered objects
    successful = download_s3_objects(
        filtered_objects,
        output_dir,
        max_concurrent=10,
        multipart_count=8,
        quiet=False
    )
    
    print(f"\nDownload complete. {successful} of {len(filtered_objects)} files downloaded successfully.")
    return successful > 0

if __name__ == "__main__":
    # Example: Download only band 5 and band 7 files
    download_specific_files(
        "https://source.coop/example-org/landsat-dataset", 
        ["_B5.", "_B7."]
    )
```

### Resumable Downloads

For large repositories, you might want to implement a resumable download that can continue after interruptions:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
from source_coop.commands.download import download_s3_objects
from pathlib import Path
import json
import os

def resumable_download(repository_url, output_dir=None, file_type=None):
    client = SourceCoopClient()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            print("Failed to convert repository URL to S3 URL.")
            return False
    else:
        s3_url = repository_url
    
    # Set default output directory if not provided
    if not output_dir:
        # Extract repository name from S3 URL
        _, prefix = SourceCoopS3.parse_s3_url(s3_url)
        repo_name = prefix.strip('/').split('/')[-1] if prefix else "download"
        output_dir = f"./source-coop-{repo_name}"
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Path for the download manifest file
    manifest_path = output_path / ".download_manifest.json"
    
    # Get objects to download
    print(f"Using S3 URL: {s3_url}")
    print("Listing objects...")
    objects, summary = client.s3.list_objects_with_summary(s3_url, file_type=file_type)
    
    if not objects:
        print("No objects found to download.")
        return False
    
    print(f"\nFound {summary['total_files']} files ({summary['total_size_human']})")
    
    # Check if we have a previous manifest
    already_downloaded = set()
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                already_downloaded = set(manifest.get('downloaded', []))
            
            print(f"Found existing manifest: {len(already_downloaded)} files already downloaded")
        except Exception as e:
            print(f"Error reading manifest file: {e}")
            already_downloaded = set()
    
    # Filter out already downloaded files
    to_download = []
    skipped = 0
    
    for obj in objects:
        key = obj['key']
        file_path = output_path / key
        
        # Skip if already in manifest or if file exists and size matches
        if key in already_downloaded and file_path.exists() and file_path.stat().st_size == obj['size']:
            skipped += 1
            continue
        
        to_download.append(obj)
    
    print(f"Skipping {skipped} already downloaded files.")
    print(f"Downloading {len(to_download)} files...")
    
    if not to_download:
        print("All files already downloaded.")
        return True
    
    # Download the remaining files
    successful = download_s3_objects(
        to_download,
        output_dir,
        max_concurrent=10,
        multipart_count=8,
        quiet=False
    )
    
    # Update manifest with newly downloaded files
    if successful > 0:
        # Add new successful downloads to our set
        for obj in to_download[:successful]:  # Assuming first 'successful' items were downloaded
            already_downloaded.add(obj['key'])
        
        # Save updated manifest
        try:
            with open(manifest_path, 'w') as f:
                json.dump({
                    'repository': s3_url,
                    'downloaded': list(already_downloaded)
                }, f, indent=2)
            print(f"Updated download manifest ({len(already_downloaded)} files recorded)")
        except Exception as e:
            print(f"Error saving manifest file: {e}")
    
    print(f"\nDownload complete. {successful} of {len(to_download)} files downloaded in this session.")
    print(f"Total downloaded: {len(already_downloaded)} of {len(objects)} files")
    
    return successful > 0 or skipped > 0

if __name__ == "__main__":
    resumable_download("https://source.coop/example-org/landsat-dataset")
```

### Interactive File Selection

For interactive applications, you might want to let the user select which files to download:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
from source_coop.commands.download import download_s3_objects
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich import print
from pathlib import Path
import re

def interactive_download(repository_url, output_dir=None):
    client = SourceCoopClient()
    console = Console()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            console.print("[red]Failed to convert repository URL to S3 URL.[/red]")
            return False
    else:
        s3_url = repository_url
    
    console.print(f"[bold]Using S3 URL:[/bold] {s3_url}")
    
    # Set default output directory if not provided
    if not output_dir:
        # Extract repository name from S3 URL
        _, prefix = SourceCoopS3.parse_s3_url(s3_url)
        repo_name = prefix.strip('/').split('/')[-1] if prefix else "download"
        output_dir = f"./source-coop-{repo_name}"
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[bold]Using output directory:[/bold] {output_dir}")
    
    # Get objects to download
    with console.status("[bold green]Listing objects...[/bold green]"):
        objects, summary = client.s3.list_objects_with_summary(s3_url)
    
    if not objects:
        console.print("[yellow]No objects found in the repository.[/yellow]")
        return False
    
    console.print(f"\n[bold]Repository Summary:[/bold]")
    console.print(f"Total Files: {summary['total_files']}")
    console.print(f"Total Size: {summary['total_size_human']}")
    
    # Group files by extension
    extensions = {}
    for ext, stats in summary['file_types'].items():
        extensions[ext] = stats
    
    # Show file type breakdown
    console.print("\n[bold]File Types:[/bold]")
    for ext, stats in sorted(extensions.items(), key=lambda x: x[1]['size'], reverse=True):
        percentage = (stats['size'] / summary['total_size'] * 100) if summary['total_size'] > 0 else 0
        console.print(f"- {ext}: {stats['count']} files, {SourceCoopS3.human_readable_size(stats['size'])} ({percentage:.2f}%)")
    
    # Prompt for download options
    console.print("\n[bold]Select files to download:[/bold]")
    console.print("1. Download all files")
    console.print("2. Download by file extension")
    console.print("3. Download by pattern match")
    console.print("4. Cancel")
    
    choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"], default="1")
    
    selected_objects = []
    
    if choice == "1":
        # Download all files
        selected_objects = objects
        console.print(f"[bold green]Selected all {len(objects)} files for download.[/bold green]")
    
    elif choice == "2":
        # Download by file extension
        console.print("\n[bold]Available extensions:[/bold]")
        ext_choices = list(extensions.keys())
        
        for i, ext in enumerate(ext_choices, 1):
            stats = extensions[ext]
            console.print(f"{i}. {ext}: {stats['count']} files, {SourceCoopS3.human_readable_size(stats['size'])}")
        
        ext_choice = Prompt.ask("Enter extension number", default="1")
        try:
            ext_index = int(ext_choice) - 1
            if 0 <= ext_index < len(ext_choices):
                selected_ext = ext_choices[ext_index]
                selected_objects = [obj for obj in objects if obj['extension'] == selected_ext]
                console.print(f"[bold green]Selected {len(selected_objects)} {selected_ext} files for download.[/bold green]")
            else:
                console.print("[red]Invalid choice.[/red]")
                return False
        except ValueError:
            console.print("[red]Invalid number.[/red]")
            return False
    
    elif choice == "3":
        # Download by pattern match
        pattern = Prompt.ask("Enter a pattern to match in filenames (e.g., 'landsat' or 'B5.TIF')")
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            selected_objects = [obj for obj in objects if regex.search(obj['key'])]
            console.print(f"[bold green]Selected {len(selected_objects)} files matching '{pattern}'.[/bold green]")
            
            if not selected_objects:
                console.print("[yellow]No files matched the pattern.[/yellow]")
                return False
        except re.error:
            console.print("[red]Invalid regular expression.[/red]")
            return False
    
    elif choice == "4":
        # Cancel
        console.print("[yellow]Download cancelled.[/yellow]")
        return False
    
    # Calculate total size
    total_size = sum(obj['size'] for obj in selected_objects)
    total_size_human = SourceCoopS3.human_readable_size(total_size)
    
    # Confirm download
    console.print(f"\nReady to download {len(selected_objects)} files ({total_size_human}) to {output_dir}")
    
    if not Confirm.ask("Continue with download?"):
        console.print("[yellow]Download cancelled.[/yellow]")
        return False
    
    # Choose download options
    max_concurrent = int(Prompt.ask("Maximum concurrent downloads", default="10"))
    multipart_count = int(Prompt.ask("Multipart count for large files (0 to disable)", default="8"))
    
    # Download the selected files
    successful = download_s3_objects(
        selected_objects,
        output_dir,
        max_concurrent=max_concurrent,
        multipart_count=multipart_count,
        quiet=False
    )
    
    console.print(f"\n[bold]Download complete. {successful} of {len(selected_objects)} files downloaded successfully.[/bold]")
    return successful > 0

if __name__ == "__main__":
    interactive_download("https://source.coop/example-org/landsat-dataset")
```

## Error Handling

When working with downloads, it's important to handle potential errors:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
from source_coop.commands.download import download_s3_objects
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_with_error_handling(repository_url, output_dir=None, file_type=None, retries=3):
    client = SourceCoopClient()
    
    try:
        # Convert repository URL to S3 URL if needed
        if repository_url.startswith("http"):
            s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
            if not s3_url:
                logger.error("Failed to convert repository URL to S3 URL.")
                return False
        else:
            s3_url = repository_url
        
        logger.info(f"Using S3 URL: {s3_url}")
        
        # Set default output directory if not provided
        if not output_dir:
            # Extract repository name from S3 URL
            _, prefix = SourceCoopS3.parse_s3_url(s3_url)
            repo_name = prefix.strip('/').split('/')[-1] if prefix else "download"
            output_dir = f"./source-coop-{repo_name}"
        
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Using output directory: {output_dir}")
        
        # Try to get objects with retries
        objects = None
        summary = None
        
        for attempt in range(retries):
            try:
                logger.info(f"Listing objects (attempt {attempt+1}/{retries})...")
                objects, summary = client.s3.list_objects_with_summary(s3_url, file_type=file_type)
                if objects:
                    break
            except Exception as e:
                logger.error(f"Error listing objects (attempt {attempt+1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    # Wait before retrying (with exponential backoff)
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
        
        if not objects:
            logger.error("Failed to list objects after multiple attempts.")
            return False
        
        logger.info(f"Found {summary['total_files']} files ({summary['total_size_human']})")
        
        # Download with retries
        for attempt in range(retries):
            try:
                logger.info(f"Starting download (attempt {attempt+1}/{retries})...")
                successful = download_s3_objects(
                    objects,
                    output_dir,
                    max_concurrent=10,
                    multipart_count=8,
                    quiet=False
                )
                
                if successful > 0:
                    logger.info(f"Download complete. {successful} of {len(objects)} files downloaded successfully.")
                    return True
                else:
                    logger.warning("No files were successfully downloaded.")
            except Exception as e:
                logger.error(f"Error during download (attempt {attempt+1}/{retries}): {str(e)}")
                
            if attempt < retries - 1:
                # Wait before retrying (with exponential backoff)
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
        
        logger.error("Download failed after multiple attempts.")
        return False
        
    except Exception as e:
        logger.error(f"Unhandled error during download process: {str(e)}")
        return False

if __name__ == "__main__":
    download_with_error_handling("https://source.coop/example-org/landsat-dataset")
```

## Best Practices

1. **Check Before Downloading**: Use `summarize` first to understand what you're getting and how large it is.

2. **Use Multipart for Large Files**: Multipart downloads significantly speed up the transfer of large files and improve reliability.

3. **Adjust Concurrency**: If your connection can handle it, increase the number of concurrent downloads to speed up the process.

4. **Filter When Appropriate**: Use file type filters to download only the specific types of data you need.

5. **Implement Resumable Downloads**: For large repositories or unreliable connections, implement a system to track downloaded files and resume interrupted downloads.

6. **Handle Rate Limiting**: Be prepared to handle rate limiting or temporary failures by implementing retries with exponential backoff.

7. **Preserve Directory Structure**: The download command preserves the directory structure from the repository, which helps maintain the organization of the data.

The download functionality is designed to efficiently transfer large amounts of data from Source Coop repositories while giving you control over the process.
