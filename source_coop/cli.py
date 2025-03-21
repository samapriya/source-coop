#!/usr/bin/env python3
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

import argparse
import logging
from pathlib import Path

from source_coop.commands import (
    login_command,
    repos_command,
    profile_command,
    members_command,
    summarize_command,
    download_command,
    whoami_command
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("source-coop")

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Source Coop CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Login command
    login_parser = subparsers.add_parser("login", help="Log in to source.coop")
    login_parser._action_groups.pop()
    login_optional = login_parser.add_argument_group('optional arguments')
    login_optional.add_argument("--email", help="Email address (will prompt if not provided)")
    login_optional.add_argument("--password", help="Password (will prompt securely if not provided)")

    # Whoami command
    subparsers.add_parser("whoami", help="Show current user info")

    # List repositories command
    repos_parser = subparsers.add_parser("repos", help="List repositories")
    repos_parser._action_groups.pop()
    repos_optional = repos_parser.add_argument_group('optional arguments')
    repos_optional.add_argument("--featured", action="store_true", help="List featured repositories")
    repos_optional.add_argument("--limit", type=int, default=10, help="Maximum number of repositories to return")
    repos_optional.add_argument("--next", help="Next page token for pagination")
    repos_optional.add_argument("--search", help="Search query to filter repositories")
    repos_optional.add_argument("--export", choices=["json", "csv", "parquet"],
                            help="Export results to specified format")
    repos_optional.add_argument("--output", help="Path for exported file (default: ./exports/source-coop-repositories-<timestamp>.<format>)")

    # Profile command
    profile_parser = subparsers.add_parser("profile", help="Get profile information")
    profile_parser._action_groups.pop()
    profile_required = profile_parser.add_argument_group('required arguments')
    profile_required.add_argument("username", help="Username or account ID")

    # Members command
    members_parser = subparsers.add_parser("members", help="Get organization members")
    members_parser._action_groups.pop()
    members_required = members_parser.add_argument_group('required arguments')
    members_required.add_argument("organization", help="Organization username or account ID")

    # Summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize repository contents")
    summarize_parser._action_groups.pop()
    summarize_required = summarize_parser.add_argument_group('required arguments')
    summarize_optional = summarize_parser.add_argument_group('optional arguments')
    summarize_required.add_argument("repository", help="Repository URL or S3 URL")
    summarize_optional.add_argument("--file-type", help="File type to filter by (e.g. '.csv')")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download repository contents")
    download_parser._action_groups.pop()
    download_required = download_parser.add_argument_group('required arguments')
    download_optional = download_parser.add_argument_group('optional arguments')
    download_required.add_argument("repository", help="Repository URL or S3 URL")
    download_optional.add_argument("--file-type", help="File type to filter by (e.g. '.csv')")
    download_optional.add_argument("--output-dir", help="Directory to save downloaded files (default: ./source-coop-<repo>)")
    download_optional.add_argument("--threads", type=int, default=10,
                               help="Maximum number of concurrent downloads (default: 10)")
    download_optional.add_argument("--multipart", type=int, default=8,
                               help="Number of parts to split large file downloads into (default: 8, 0 to disable)")
    download_optional.add_argument("--quiet", action="store_true",
                               help="Don't ask for confirmation and don't display file list")

    args = parser.parse_args()

    # Process commands
    if args.command == "login":
        login_command(args.email, args.password)
    elif args.command == "whoami":
        whoami_command()
    elif args.command == "repos":
        repos_command(args.featured, args.limit, args.next, args.search,
                     export_format=args.export, output_path=args.output)
    elif args.command == "profile":
        profile_command(args.username)
    elif args.command == "members":
        members_command(args.organization)
    elif args.command == "summarize":
        summarize_command(args.repository, args.file_type)
    elif args.command == "download":
        download_command(args.repository, args.file_type, args.output_dir,
                        args.threads, args.multipart, args.quiet)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
