# CLI Reference

This page provides a comprehensive reference for all command-line interface (CLI) commands available in the Source Coop tool.

## Command Structure

All commands follow this general structure:

```bash
source-coop COMMAND [OPTIONS]
```

## Global Help

To see the full list of available commands:

```bash
source-coop --help
```

Example output:

```
usage: source-coop [-h] {login,whoami,repos,profile,members,summarize,download} ...

Source Coop CLI

positional arguments:
  {login,whoami,repos,profile,members,summarize,download}
                        Command to run
    login               Log in to source.coop
    whoami              Show current user info
    repos               List repositories
    profile             Get profile information
    members             Get organization members
    summarize           Summarize repository contents
    download            Download repository contents

options:
  -h, --help            show this help message and exit
```

## Commands

### login

Log in to Source Coop and save authentication cookies.

```bash
source-coop login [--email EMAIL] [--password PASSWORD]
```

| Option | Description |
|--------|-------------|
| `--email` | Email address (will prompt if not provided) |
| `--password` | Password (will prompt securely if not provided) |

### whoami

Check who you're currently logged in as.

```bash
source-coop whoami
```

This command has no options. It displays information about the currently authenticated user.

### repos

List Source Coop repositories.

```bash
source-coop repos [--featured] [--limit LIMIT] [--next NEXT] [--search SEARCH] [--export {json,csv,parquet}] [--output OUTPUT]
```

| Option | Description |
|--------|-------------|
| `--featured` | List featured repositories |
| `--limit` | Maximum number of repositories to return (default: 10) |
| `--next` | Next page token for pagination |
| `--search` | Search query to filter repositories |
| `--export` | Export results to specified format (`json`, `csv`, or `parquet`) |
| `--output` | Path for exported file (default: ./exports/source-coop-repositories-<timestamp>.<format>) |

### profile

Get profile information for a user or organization.

```bash
source-coop profile USERNAME
```

| Argument | Description |
|----------|-------------|
| `USERNAME` | Username or account ID |

### members

Get members of an organization.

```bash
source-coop members ORGANIZATION
```

| Argument | Description |
|----------|-------------|
| `ORGANIZATION` | Organization username or account ID |

### summarize

Summarize repository contents without downloading.

```bash
source-coop summarize REPOSITORY [--file-type FILE_TYPE]
```

| Argument/Option | Description |
|-----------------|-------------|
| `REPOSITORY` | Repository URL or S3 URL |
| `--file-type` | File type to filter by (e.g. '.csv') |

### download

Download repository contents.

```bash
source-coop download REPOSITORY [--file-type FILE_TYPE] [--output-dir OUTPUT_DIR] [--threads THREADS] [--multipart MULTIPART] [--quiet]
```

| Argument/Option | Description |
|-----------------|-------------|
| `REPOSITORY` | Repository URL or S3 URL |
| `--file-type` | File type to filter by (e.g. '.csv') |
| `--output-dir` | Directory to save downloaded files (default: ./source-coop-<repo>) |
| `--threads` | Maximum number of concurrent downloads (default: 10) |
| `--multipart` | Number of parts to split large file downloads into (default: 8, 0 to disable) |
| `--quiet` | Don't ask for confirmation and don't display file list |

## URL Formats

The `summarize` and `download` commands accept both web URLs and S3 URLs:

- **Web URL format**: `https://source.coop/ACCOUNT/REPOSITORY`
- **S3 URL format**: `s3://ACCOUNT/REPOSITORY`

The tool automatically converts between these formats, so you can use whichever is more convenient.

## Common Command Patterns

### Viewing repository contents before downloading

```bash
# First, summarize the repository to see what's in it
source-coop summarize https://source.coop/account/repository

# Then, download specific file types of interest
source-coop download https://source.coop/account/repository --file-type .tif
```

### Exporting repository metadata for analysis

```bash
# Export repository information to CSV
source-coop repos --search "landsat" --export csv --output landsat-repos.csv
```

### Downloading with increased parallelism for speed

```bash
# Use more threads and parts for faster downloads
source-coop download s3://account/repository --threads 20 --multipart 16
```

### Scripted/automated downloads

```bash
# Use quiet mode for scripted operations
source-coop download s3://account/repository --quiet
```

## Environment Variables

The Source Coop CLI does not currently use environment variables for configuration. All settings are controlled via command-line options.

## Exit Codes

The CLI returns standard exit codes:

- `0`: Command completed successfully
- Non-zero: Command failed (exact code depends on the nature of the failure)

You can check the exit code in scripts with `$?` (bash) or `$LASTEXITCODE` (PowerShell).

## Configuration Files

The Source Coop CLI stores its configuration in the following locations:

- **Authentication cookies**: `~/.config/source-coop/cookies.json` (Linux/macOS) or similar paths on other platforms

This file contains authentication tokens needed to access Source Coop without re-entering your credentials.
