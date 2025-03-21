# Unofficial Source Coop Python SDK & CLI
![License](https://img.shields.io/badge/License-Apache%202.0-blue)

<center>

<img src="https://github.com/user-attachments/assets/d0441aa4-f491-464b-ae1f-b994dc8a0b65" alt="Logo" width="150">

</center>

An unofficial Python SDK and command-line interface for [Source Coop](https://source.coop), a platform for discovering, accessing, and sharing geospatial data.

!!! tip "Insiders Program and Insiders only datasets"

    **DISCLAIMER: This project is not officially affiliated with, authorized by, endorsed by, or in any way connected to Source Coop or Radiant Earth. This is an independent project created by Samapriya Roy to simplify interaction with Source Coop's public APIs and services**

## What is Source Coop?

Source Coop is a platform for sharing and discovering geospatial datasets. It provides a centralized repository where organizations and individuals can publish, find, and access geospatial data in various formats.

## Why This Tool Exists

This Python SDK and CLI was developed to simplify programmatic interaction with Source Coop. While Source Coop provides a web interface for browsing and downloading data, many geospatial data workflows benefit from automation and integration into existing data pipelines.

This tool enables you to:

- Script the discovery and downloading of datasets
- Incorporate Source Coop datasets into automated workflows
- Efficiently download large datasets with multipart and concurrent transfer support
- Explore and search repositories programmatically

## Features

This package serves both as a software development kit (SDK) for Python applications and as a command-line interface (CLI):

- **Authentication**: Log in to Source Coop and manage your session
- **Repository Discovery**: Browse, search, and export repository information
- **Account Information**: Retrieve profile details for users and organizations
- **Content Exploration**: List and summarize repository contents without downloading
- **Efficient Downloads**: Download repository data with concurrent and multipart support for large files
- **Python Integration**: Import the package in your Python applications for programmatic access
- **Command-Line Interface**: Use the CLI for quick operations without writing code

## Key Components

The tool is organized into several components:

- **Client**: The main entry point for Python SDK usage, integrating API and S3 functionality
- **API Client**: Handles REST API interactions for accounts, repositories, and metadata
- **S3 Client**: Manages interaction with Source Coop's S3-compatible storage
- **Authentication**: Handles login and session management
- **CLI**: Command-line interface for all functionality

## Who Should Use This Tool

This tool is ideal for:

- **GIS Analysts**: Who need to download and process geospatial data
- **Data Scientists**: Working with geospatial datasets in automated pipelines
- **Researchers**: Accessing and analyzing geospatial data programmatically
- **Developers**: Building applications that incorporate Source Coop data

## Getting Started

To start using the tool, check out the following guides:

- [Installation](https://source.geocarpentry.org/installation): How to install the package
- [Authentication](https://source.geocarpentry.org/login): How to log in and verify your identity
- [Repository Discovery](https://source.geocarpentry.org/repos): How to find and explore repositories
- [Downloading Data](https://source.geocarpentry.org/download): How to efficiently download repository content

For a complete list of commands and their options, see the [CLI Reference](https://source.geocarpentry.org/cli-reference).
