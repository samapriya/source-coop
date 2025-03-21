# Unofficial Source Coop Python SDK and CLI

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

| <img src="https://github.com/user-attachments/assets/d0441aa4-f491-464b-ae1f-b994dc8a0b65" alt="Logo" width="50"> | **Python SDK and CLI** <br> ![License](https://img.shields.io/badge/License-Apache%202.0-blue) |
|---|---|

An unofficial Python SDK and command-line interface for [Source Coop](https://source.coop), a platform for sharing geospatial data.

> **DISCLAIMER**: This project is not officially affiliated with, authorized by, endorsed by, or in any way connected to Source Coop or Radiant Earth. This is an independent project created by Samapriya Roy to simplify interaction with Source Coop's public APIs and services.


# For complete documentation head to [source.geocarpnetry.org](https://source.geocarpentry.org/)

## Features

This package serves both as a software development kit (SDK) for Python applications and as a command-line interface (CLI):

- **As an SDK**: Import the package in your Python applications to interact with Source Coop programmatically
- **As a CLI**: Use the command-line interface for quick operations without writing code

The package provides functionality for:

- Authenticating with Source Coop
- Browsing and searching repositories
- Retrieving account and organization profiles
- Listing and summarizing repository contents
- Downloading data from repositories with concurrent and multipart support

## Installation

Install the package using pip to get both the Python SDK and the command-line tool:

```bash
pip install source-coop
```

## Command-Line Interface

The CLI provides several commands to interact with Source Coop. Each command has specific options that can be discovered using the `--help` flag.

### Authentication

Authentication is required for accessing certain features of Source Coop. The CLI provides commands to log in and verify your identity.

```bash
# Log in to Source Coop (will prompt for credentials)
source-coop login

# Check who you're logged in as
source-coop whoami
```

When you run the login command, you'll be prompted for your Source Coop email and password. Your credentials are securely saved as cookies in your user directory for future use. The `whoami` command helps verify that you're logged in correctly by displaying your profile information.

### Exploring Repositories

Source Coop hosts numerous geospatial data repositories. These commands help you discover and search through available datasets.

```bash
# List recent repositories
source-coop repos

# List featured repositories
source-coop repos --featured

# Search for repositories
source-coop repos --search "sentinel"

# Export repository list to CSV
source-coop repos --export csv --output my-repos.csv
```

The `repos` command without arguments lists recent repositories with details like title, account, tags, and publication date. The `--featured` flag shows highlighted repositories chosen by Source Coop. Use the search functionality to find repositories containing specific keywords. You can export the results to CSV, JSON, or Parquet format for further analysis or record-keeping.

### Account Information

These commands provide details about user profiles and organization memberships on Source Coop.

```bash
# Get profile information for a user or organization
source-coop profile username

# List members of an organization
source-coop members organization_name
```

The `profile` command displays information about a specific user or organization, including their bio and associated repositories. For organizations, the `members` command reveals the organizational structure by listing all members and their roles, which is useful for understanding who contributes to a specific group's repositories.

### Repository Operations

Once you've found repositories of interest, these commands help you explore their contents and download data. You can use either web URLs or S3 URLs interchangeably - the CLI will handle the conversion for you.

```bash
# Summarize repository contents (using web URL)
source-coop summarize https://source.coop/account/repository

# Filter by file type (using S3 URL)
source-coop summarize s3://account/repository --file-type .tif

# Download repository contents (using web URL)
source-coop download https://source.coop/account/repository

# Download with custom options (using S3 URL)
source-coop download s3://account/repository \
  --file-type .csv \
  --output-dir ./data \
  --threads 20 \
  --multipart 16
```

The `summarize` command provides a quick overview of a repository's contents, showing file counts, sizes, and types without downloading anything. This helps you understand what's in a repository before committing to a download. The command accepts both web URLs and S3-style URLs.

The `download` command efficiently retrieves files from a repository. It supports concurrent downloads to speed up the process and multipart downloads for large files. You can filter by file type to download only the data you need and specify an output directory to organize your downloads.

### CLI Help

For detailed help on any command:

```bash
source-coop --help
source-coop command --help  # e.g., source-coop download --help
```

Each command has additional options not covered here. Use the help system to discover all available features.

## Python SDK Usage

The SDK provides programmatic access to Source Coop's features, allowing you to incorporate them into your own Python applications.

### Client Setup

The main entry point for the SDK is the `SourceCoopClient` class, which handles both API and S3 operations.

```python
from source_coop import SourceCoopClient

# Create a client (will use stored credentials if available)
client = SourceCoopClient()

# Check if authenticated
if client.is_authenticated():
    print("Client is authenticated")
else:
    print("Client is not authenticated, use login_to_source_coop() first")
```

When you initialize a client, it automatically looks for stored cookies from previous logins. The `is_authenticated()` method helps you verify whether the client has valid authentication credentials before attempting operations that might require them. This is useful for scripts that need to check authentication status before proceeding.

### Authentication

If your application needs to log in programmatically, you can use the authentication functions directly.

```python
from source_coop import login_to_source_coop

# Log in and save credentials
cookies = login_to_source_coop("email@example.com", "password")

# Create a client with the cookies
from source_coop import SourceCoopClient
client = SourceCoopClient(cookies)
```

The `login_to_source_coop` function handles the authentication flow with Source Coop's servers and returns cookies that can be used to create an authenticated client. These cookies are also saved to your filesystem for future use. This approach is particularly useful for automated scripts or applications where you want to handle authentication programmatically rather than through the CLI.

### Working with Repositories

The API client provides methods for discovering and searching repositories.

```python
# Get repositories
repos_data = client.api.get_repositories(limit=20)

# Search repositories
search_results = client.api.get_repositories(search="landsat")

# Get featured repositories
featured = client.api.get_repositories(featured=True)
```

These methods return structured data about repositories, including metadata like titles, descriptions, tags, and publication dates. The `limit` parameter controls how many results are returned, which is useful for pagination. The `search` parameter filters repositories based on keywords, helping you find relevant datasets. The `featured` flag returns repositories that have been highlighted by Source Coop for their significance or quality.

### Accessing Account Information

The API client also provides methods for accessing account information.

```python
# Get your own account info
profile = client.api.whoami()

# Get another account's profile
user_profile = client.api.get_profile("username")

# Get organization members
members = client.api.get_members("organization_name")
```

The `whoami` method returns information about your own account, which is useful for verifying authentication and accessing your profile data. The `get_profile` method retrieves public information about any account, which can help you learn more about data providers. For organizational accounts, the `get_members` method shows the membership structure, revealing who contributes to an organization's repositories.

### Working with S3 Data

The S3 client provides methods for interacting with the actual data in repositories.

```python
# List objects in a repository
s3_url = "s3://account/repository"
s3_objects = client.s3.list_objects(s3_url)

# List with filtering by file type
tiff_objects = client.s3.list_objects(s3_url, file_type=".tif")

# Get summary statistics
objects, summary = client.s3.list_objects_with_summary(s3_url)
print(f"Total files: {summary['total_files']}")
print(f"Total size: {summary['total_size_human']}")
```

The `list_objects` method retrieves detailed information about files in a repository, including their names, sizes, and download URLs. You can filter by file extension to focus on specific data types. The `list_objects_with_summary` method provides additional aggregated statistics about the repository, such as total file count, total size, and a breakdown by file type. This is useful for understanding the composition of a repository before downloading any files.

### URL Handling (Web URLs and S3 URLs)

Source Coop supports both web URLs (https://source.coop/account/repository) and S3-style URLs (s3://account/repository). The SDK handles both formats seamlessly, so you can use whichever is more convenient.

```python
from source_coop import SourceCoopClient

client = SourceCoopClient()

# You can use regular web URLs directly with most methods
repository_url = "https://source.coop/account/repository"
objects, summary = client.s3.list_objects_with_summary(repository_url)

# Or you can use S3-style URLs if you prefer
s3_url = "s3://account/repository"
objects, summary = client.s3.list_objects_with_summary(s3_url)

# If you need to convert between formats for any reason:
from source_coop.s3 import SourceCoopS3
converted_url = SourceCoopS3.convert_repo_url_to_s3_url(repository_url)
```

Most SDK methods automatically handle URL conversion internally, so you can provide either format. This makes the SDK more intuitive to use since you can simply copy and paste URLs from your browser. Behind the scenes, the SDK converts web URLs to the S3 format when necessary, but this is transparent to you as a user.

## Real-World Example: Downloading PMTiles Files

This complete example demonstrates downloading PMTiles files from a real public repository. The code uses web URLs directly without needing to manually convert them to S3 URLs.

```python
from pathlib import Path

from source_coop import SourceCoopClient
from source_coop.commands.download import download_s3_objects


def main():
    # Repository URL - this is a real public repository with PMTiles data
    repository_url = "https://source.coop/fiboa/japan"

    # Output directory
    output_dir = "downloaded-pmtiles"

    # Create a client
    client = SourceCoopClient()

    # Check if we're authenticated
    if not client.is_authenticated():
        print("Not authenticated. Please run 'source-coop login' first")
        return

    print(f"Downloading PMTiles from: {repository_url}")

    # List objects and get summary, filtering for .pmtiles files
    # Note: We're using the web URL directly here - no manual conversion needed!
    print("Listing PMTiles files...")
    objects, summary = client.s3.list_objects_with_summary(repository_url, file_type=".pmtiles")

    if not objects:
        print("No PMTiles files found in the repository")
        return

    # Display summary
    total_files = summary['total_files']
    total_size = summary['total_size_human']
    print(f"Found {total_files} PMTiles files (Total size: {total_size})")

    # Display first few files
    if objects:
        print("\nFiles to download:")
        for i, obj in enumerate(objects[:5]):
            print(f"- {obj['key']} ({client.s3.human_readable_size(obj['size'])})")
        if len(objects) > 5:
            print(f"- ... and {len(objects) - 5} more files")

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Download the files
    successful = download_s3_objects(
        objects,
        output_dir,
        multipart_count=8,  # Use multipart downloads for large files
        max_concurrent=10   # Use up to 10 concurrent downloads
    )

    print(f"Successfully downloaded {successful} PMTiles files to {output_dir}")


if __name__ == "__main__":
    main()
```

This example demonstrates several key features:

1. **Direct use of web URLs**: The code uses a standard web URL directly with SDK methods
2. **File type filtering**: It only lists files with the `.pmtiles` extension
3. **User-friendly output**: It shows a summary and previews files before downloading
4. **Efficient downloading**: It uses multipart downloading for large files and handles up to 10 concurrent downloads

You can run this exact code to download real PMTiles files from a public repository. The SDK handles all the complexities of URL conversion, API interactions, and efficient downloading behind the scenes.

The `download_s3_objects` function handles the complex process of downloading multiple files concurrently while showing progress bars. The `max_concurrent` parameter controls how many files are downloaded simultaneously, while `multipart_count` determines how many parts large files are split into for parallel downloading. This approach significantly speeds up downloads, especially for repositories with many files or very large files.

## Configuration

The package stores configuration in the following location:

- **Authentication cookies**: `~/.config/source-coop/cookies.json`

This file contains authentication tokens needed to access Source Coop without re-entering your credentials. The cookies are securely stored and automatically used when you create a new client.

## License

This project is licensed under the Apache License 2.0 - see the file headers for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- This package is developed by [Samapriya Roy](https://github.com/samapriya)
- Thanks to Source Coop for providing a platform for sharing geospatial data
