# Summarizing Repository Contents

The `summarize` command allows you to analyze the contents of a Source Coop repository without downloading any files. This is useful for understanding what's in a repository, including file counts, sizes, types, and other metadata, before deciding whether to download files.

## CLI Usage

To summarize the contents of a repository:

```bash
source-coop summarize REPOSITORY_URL
```

You can use either a web URL (https://source.coop/account/repository) or an S3 URL (s3://account/repository).

### Filtering by File Type

You can filter the summary to show only files of a specific type:

```bash
source-coop summarize REPOSITORY_URL --file-type .tif
```

This will only include files with the specified extension (e.g., `.tif`, `.csv`, `.json`) in the summary.

### Example Output

```
Using S3 URL: s3://example-org/landsat-dataset

Listing objects...

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repository Summary         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Metric     │ Value         │
├────────────┼───────────────┤
│ Total Files│ 156           │
│ Total Size │ 2.34 GB       │
└────────────┴───────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File Types Breakdown       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Extension │ Count │ Size   │ Percentage │
├───────────┼───────┼────────┼────────────┤
│ .tif      │ 120   │ 2.1 GB │ 89.74%     │
│ .xml      │ 24    │ 150 MB │ 6.41%      │
│ .json     │ 12    │ 90 MB  │ 3.85%      │
└───────────┴───────┴────────┴────────────┘

Objects (showing 20 of 156)
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Last Modified    ┃ Size    ┃ Key                                                                            ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2024-03-15 14:30 │ 25.6 MB │ landsat-dataset/scene1/LC08_L2SP_202033_20240301_20240305_02_T1_SR_B5.TIF     │
│ 2024-03-15 14:30 │ 25.3 MB │ landsat-dataset/scene1/LC08_L2SP_202033_20240301_20240305_02_T1_SR_B4.TIF     │
│ ...              │ ...     │ ...                                                                            │
└──────────────────┴─────────┴────────────────────────────────────────────────────────────────────────────────┘
```

The output includes:
1. A repository summary with total file count and size
2. A breakdown of file types showing count, size, and percentage
3. A list of the most recent files in the repository

### CLI Help

For more options and help:

```bash
source-coop summarize --help
```

## Python SDK Usage

### Basic Repository Summary

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3

def summarize_repository(repository_url):
    # Create a client instance
    client = SourceCoopClient()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            print("Failed to convert repository URL to S3 URL.")
            return None
    else:
        s3_url = repository_url
    
    print(f"Using S3 URL: {s3_url}")
    print("Listing objects...")
    
    # Get objects and summary
    objects, summary = client.s3.list_objects_with_summary(s3_url)
    
    if not objects:
        print("No objects found in the repository.")
        return None
    
    # Print summary information
    print(f"\nRepository Summary:")
    print(f"Total Files: {summary['total_files']}")
    print(f"Total Size: {summary['total_size_human']}")
    
    # Print file type breakdown
    print("\nFile Types Breakdown:")
    for ext, stats in sorted(summary['file_types'].items(), key=lambda x: x[1]['size'], reverse=True):
        percentage = (stats['size'] / summary['total_size'] * 100) if summary['total_size'] > 0 else 0
        print(f"- {ext}: {stats['count']} files, {SourceCoopS3.human_readable_size(stats['size'])} ({percentage:.2f}%)")
    
    # Print some of the objects
    print(f"\nRecent Files (showing up to 5):")
    sorted_objects = sorted(objects, key=lambda x: x['last_modified'], reverse=True)
    for obj in sorted_objects[:5]:
        print(f"- {obj['key']} ({SourceCoopS3.human_readable_size(obj['size'])})")
    
    return {
        'objects': objects,
        'summary': summary
    }

if __name__ == "__main__":
    summarize_repository("https://source.coop/example-org/landsat-dataset")
```

### Filtering by File Type

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3

def summarize_by_file_type(repository_url, file_type):
    client = SourceCoopClient()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            print("Failed to convert repository URL to S3 URL.")
            return None
    else:
        s3_url = repository_url
    
    print(f"Using S3 URL: {s3_url}")
    print(f"Filtering for files with extension: {file_type}")
    
    # Get objects and summary with file type filter
    objects, summary = client.s3.list_objects_with_summary(s3_url, file_type=file_type)
    
    if not objects:
        print(f"No {file_type} files found in the repository.")
        return None
    
    # Print summary information
    print(f"\nRepository Summary (filtered to {file_type} files):")
    print(f"Total Files: {summary['total_files']}")
    print(f"Total Size: {summary['total_size_human']}")
    
    # Print some of the objects
    print(f"\nRecent {file_type} Files (showing up to 10):")
    sorted_objects = sorted(objects, key=lambda x: x['last_modified'], reverse=True)
    for obj in sorted_objects[:10]:
        print(f"- {obj['key']} ({SourceCoopS3.human_readable_size(obj['size'])})")
    
    return {
        'objects': objects,
        'summary': summary
    }

if __name__ == "__main__":
    summarize_by_file_type("https://source.coop/example-org/landsat-dataset", ".tif")
```

### Using Rich for Formatted Output

For more visually appealing output, you can use the `rich` library to format tables and text:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
from rich.console import Console
from rich.table import Table
from rich import box

def summarize_with_rich(repository_url, file_type=None):
    client = SourceCoopClient()
    console = Console()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            console.print("[red]Failed to convert repository URL to S3 URL.[/red]")
            return None
    else:
        s3_url = repository_url
    
    console.print(f"[bold]Using S3 URL:[/bold] {s3_url}")
    
    # Filter message if applicable
    if file_type:
        console.print(f"[bold]Filtering for files with extension:[/bold] {file_type}")
    
    console.print("[bold]Listing objects...[/bold]")
    
    # Get objects and summary
    objects, summary = client.s3.list_objects_with_summary(s3_url, file_type=file_type)
    
    if not objects:
        console.print("[yellow]No objects found in the repository.[/yellow]")
        return None
    
    # Create summary table
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
    
    # Create file types table
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
                SourceCoopS3.human_readable_size(stats['size']),
                f"{percentage:.2f}%"
            )
        
        console.print(types_table)
    
    # Create objects table (limited to 20 items)
    objects_limit = 20
    objects_table = Table(
        title=f"Objects (showing {min(objects_limit, len(objects))} of {len(objects)})",
        show_header=True,
        header_style="bold blue",
        box=box.ROUNDED
    )
    
    objects_table.add_column("Last Modified", style="cyan", no_wrap=True)
    objects_table.add_column("Size", style="green", justify="right")
    objects_table.add_column("Key", style="yellow", overflow="fold")
    
    # Sort by last modified (newest first)
    sorted_objects = sorted(
        objects,
        key=lambda x: x['last_modified'],
        reverse=True
    )
    
    # Add rows (limited to specified number)
    for obj in sorted_objects[:objects_limit]:
        objects_table.add_row(
            obj['last_modified'],
            SourceCoopS3.human_readable_size(obj['size']),
            obj['key']
        )
    
    console.print(objects_table)
    
    return {
        'objects': objects,
        'summary': summary
    }

if __name__ == "__main__":
    summarize_with_rich("https://source.coop/example-org/landsat-dataset")
```

### Analyzing Repository Structure

You can use the summarize functionality to analyze the directory structure of a repository:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
from collections import defaultdict
import os

def analyze_repository_structure(repository_url):
    client = SourceCoopClient()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            print("Failed to convert repository URL to S3 URL.")
            return None
    else:
        s3_url = repository_url
    
    print(f"Using S3 URL: {s3_url}")
    print("Analyzing repository structure...")
    
    # Get objects
    objects, _ = client.s3.list_objects_with_summary(s3_url)
    
    if not objects:
        print("No objects found in the repository.")
        return None
    
    # Analyze directory structure
    directories = defaultdict(int)
    
    for obj in objects:
        key = obj['key']
        
        # Skip the object itself and process its parent directories
        path_parts = key.split('/')
        
        # Process each directory level
        for i in range(len(path_parts)):
            if i > 0:  # Skip the file itself (last part)
                dir_path = '/'.join(path_parts[:i])
                if dir_path:  # Skip empty strings
                    directories[dir_path] += 1
    
    # Print directory structure (sorted by count)
    print("\nDirectory Structure:")
    sorted_dirs = sorted(directories.items(), key=lambda x: x[1], reverse=True)
    
    for dir_path, count in sorted_dirs[:20]:  # Show top 20 directories
        depth = dir_path.count('/') + 1
        indent = '  ' * depth
        print(f"{indent}- {os.path.basename(dir_path)}/ ({count} files)")
    
    if len(sorted_dirs) > 20:
        print(f"... and {len(sorted_dirs) - 20} more directories")
    
    # Count files at the root level
    root_files = sum(1 for obj in objects if '/' not in obj['key'])
    if root_files > 0:
        print(f"\nFiles at root level: {root_files}")
    
    return {
        'objects': objects,
        'directories': dict(directories)
    }

if __name__ == "__main__":
    analyze_repository_structure("https://source.coop/example-org/landsat-dataset")
```

### Finding Largest Files

You can use the summary functionality to identify the largest files in a repository:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3

def find_largest_files(repository_url, limit=10):
    client = SourceCoopClient()
    
    # Convert repository URL to S3 URL if needed
    if repository_url.startswith("http"):
        s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
        if not s3_url:
            print("Failed to convert repository URL to S3 URL.")
            return None
    else:
        s3_url = repository_url
    
    print(f"Finding the {limit} largest files in {s3_url}...")
    
    # Get objects
    objects, _ = client.s3.list_objects_with_summary(s3_url)
    
    if not objects:
        print("No objects found in the repository.")
        return None
    
    # Sort by size (largest first)
    sorted_objects = sorted(objects, key=lambda x: x['size'], reverse=True)
    
    # Show largest files
    print(f"\nLargest files in the repository:")
    for i, obj in enumerate(sorted_objects[:limit], 1):
        print(f"{i}. {obj['key']} ({SourceCoopS3.human_readable_size(obj['size'])})")
    
    return sorted_objects[:limit]

if __name__ == "__main__":
    find_largest_files("https://source.coop/example-org/landsat-dataset")
```

## Error Handling

When working with the summary functionality, it's important to handle potential errors:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_with_error_handling(repository_url, file_type=None):
    client = SourceCoopClient()
    
    try:
        # Convert repository URL to S3 URL if needed
        if repository_url.startswith("http"):
            s3_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
            if not s3_url:
                logger.error("Failed to convert repository URL to S3 URL.")
                return None
        else:
            s3_url = repository_url
        
        logger.info(f"Using S3 URL: {s3_url}")
        
        # Get objects and summary
        objects, summary = client.s3.list_objects_with_summary(s3_url, file_type=file_type)
        
        if not objects:
            logger.warning(f"No objects found in the repository{' matching filter' if file_type else ''}.")
            return None
        
        logger.info(f"Found {summary['total_files']} files ({summary['total_size_human']}).")
        return {
            'objects': objects,
            'summary': summary
        }
        
    except Exception as e:
        logger.error(f"Error summarizing repository {repository_url}: {str(e)}")
        return None

if __name__ == "__main__":
    summarize_with_error_handling("https://source.coop/example-org/landsat-dataset")
```

## Best Practices

1. **Check Before Downloading**: Always use `summarize` before `download` to understand what you're getting and how large it is.

2. **Filter When Needed**: Use the file type filter to focus on specific data types when repositories contain mixed content.

3. **Handle Empty Results**: Be prepared for empty results, especially when using filters.

4. **URL Flexibility**: The API accepts both web URLs and S3 URLs, so use whichever is more convenient.

5. **Structure Analysis**: For large repositories, analyze the directory structure to understand the organization.

The summarize functionality is a powerful tool for exploring repository contents without downloading any data, helping you make informed decisions about which datasets to download and use in your projects.
