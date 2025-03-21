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
import os
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

import boto3
import botocore.exceptions
from botocore.config import Config

logger = logging.getLogger("source-coop.s3")

class SourceCoopS3:
    """S3 client for Source Coop"""

    ENDPOINT_URL = "https://data.source.coop"

    def __init__(self, config=None):
        """
        Initialize the S3 client

        Args:
            config (botocore.config.Config, optional): Custom boto3 configuration
        """
        # Use provided config or create a default one with retries
        self.config = config or Config(
            retries={
                'max_attempts': 5,
                'mode': 'standard'  # Uses exponential backoff
            },
            s3={'addressing_style': 'path'}
        )

        # Create the S3 client
        self.client = boto3.client(
            's3',
            endpoint_url=self.ENDPOINT_URL,
            config=self.config,
            # Public access, so no credentials needed
            aws_access_key_id='',
            aws_secret_access_key=''
        )

    @staticmethod
    def human_readable_size(size_bytes):
        """
        Convert size in bytes to human-readable format

        Args:
            size_bytes (int): Size in bytes

        Returns:
            str: Human-readable size (e.g., '1.23 GB')
        """
        if size_bytes == 0:
            return "0 B"

        size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.2f} {size_names[i]}"

    @staticmethod
    def parse_s3_url(s3_url):
        """
        Parse an S3 URL into bucket and prefix

        Args:
            s3_url (str): S3 URL in the format s3://bucket/prefix

        Returns:
            tuple: (bucket, prefix)
        """
        # Remove the s3:// prefix
        path = s3_url.replace('s3://', '')
        # Split the path into bucket and prefix
        parts = path.split('/', 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ''
        return bucket, prefix

    @staticmethod
    def convert_repo_url_to_s3_url(repo_url):
        """
        Convert a repository URL to an S3 URL

        Args:
            repo_url (str): Repository URL in the format https://source.coop/repositories/account/repository
                            or https://source.coop/account/repository

        Returns:
            str: S3 URL in the format s3://account/repository
        """
        try:
            # Parse the URL
            parsed_url = urlparse(repo_url)

            # Extract the path
            path = parsed_url.path

            # Remove /repositories/ prefix if present
            if '/repositories/' in path:
                path = path.replace('/repositories/', '')

            # Split into parts
            parts = path.strip('/').split('/')

            # If we have at least 2 parts, we can create an S3 URL
            if len(parts) >= 2:
                s3_url = f"s3://{parts[0]}/{'/'.join(parts[1:])}"
                return s3_url
            # If only 1 part, use it as the bucket name
            elif len(parts) == 1:
                s3_url = f"s3://{parts[0]}"
                return s3_url
            else:
                logger.error("Invalid repository URL format")
                return None

        except Exception as e:
            logger.error(f"Error converting repository URL to S3 URL: {e}")
            return None

    def list_objects(self, s3_url, file_type=None):
        """
        List objects from an S3-compatible storage
        Optionally filter by file type

        Args:
            s3_url (str): S3 URL in the format s3://bucket/prefix
            file_type (str, optional): File extension to filter by (e.g. '.csv')

        Returns:
            list: List of S3 objects with metadata
        """
        bucket, prefix = self.parse_s3_url(s3_url)
        s3_objects = []

        try:
            # Initialize pagination
            paginator = self.client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=bucket,
                Prefix=prefix
            )

            # Process each page of results
            for page in page_iterator:
                # Process each object in the page
                for obj in page.get('Contents', []):
                    last_modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                    size = obj['Size']
                    key = obj['Key']

                    # Generate a direct URL for the object
                    download_url = f"{self.ENDPOINT_URL}/{bucket}/{key}"

                    # Extract file extension
                    obj_ext = os.path.splitext(key)[-1].lower()

                    # Skip if file type filter is provided and doesn't match
                    if file_type and file_type.lower() != obj_ext:
                        continue

                    # Add to objects list
                    s3_objects.append({
                        'last_modified': last_modified,
                        'size': size,
                        'key': key,
                        'download_url': download_url,
                        'extension': obj_ext
                    })

            return s3_objects

        except Exception as e:
            logger.error(f"Error listing S3 objects: {e}")
            return []

    def get_summary(self, s3_objects):
        """
        Generate summary statistics for a list of S3 objects

        Args:
            s3_objects (list): List of S3 objects from list_objects

        Returns:
            dict: Summary statistics including file count and total size
        """
        # Initialize counters for summary
        total_files = len(s3_objects)
        total_size = sum(obj['size'] for obj in s3_objects)
        file_types = defaultdict(lambda: {'count': 0, 'size': 0})

        # Process each object
        for obj in s3_objects:
            # Update file type statistics
            file_ext = obj['extension'] if obj['extension'] else "(no extension)"
            file_types[file_ext]['count'] += 1
            file_types[file_ext]['size'] += obj['size']

        # Create summary statistics
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_human': self.human_readable_size(total_size),
            'file_types': dict(file_types)
        }

    def list_objects_with_summary(self, s3_url, file_type=None):
        """
        List objects from an S3-compatible storage and generate summary statistics
        Optionally filter by file type

        Args:
            s3_url (str): S3 URL in the format s3://bucket/prefix
            file_type (str, optional): File extension to filter by (e.g. '.csv')

        Returns:
            tuple: (s3_objects, summary)
                s3_objects (list): List of S3 objects
                summary (dict): Summary statistics including file count and total size
        """
        s3_objects = self.list_objects(s3_url, file_type)
        summary = self.get_summary(s3_objects)
        return s3_objects, summary
