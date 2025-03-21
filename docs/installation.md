# Installation

This guide covers how to install the Source Coop Python SDK and CLI. The package can be installed either directly into your Python environment or within a virtual environment for better isolation.

## Requirements

The Source Coop package requires:

- Python 3.7 or higher
- pip (Python package manager)

## Installing with pip

The simplest way to install the package is using pip:

```bash
pip install source-coop
```

This will install the Source Coop package along with all its dependencies.

## Installing in a Virtual Environment

For better isolation and to avoid potential conflicts with other packages, it's recommended to install the Source Coop package within a virtual environment.

### Using venv (Python's built-in virtual environment)

1. Create a new virtual environment:

```bash
# macOS/Linux
python3 -m venv source-coop-env

# Windows
python -m venv source-coop-env
```

2. Activate the virtual environment:

```bash
# macOS/Linux
source source-coop-env/bin/activate

# Windows
source-coop-env\Scripts\activate
```

3. Install the package within the virtual environment:

```bash
pip install source-coop
```

### Using conda (if you use Anaconda/Miniconda)

1. Create a new conda environment:

```bash
conda create -n source-coop-env python=3.9
```

2. Activate the conda environment:

```bash
conda activate source-coop-env
```

3. Install the package:

```bash
pip install source-coop
```

## Installing from Source

If you want to install the latest development version or make modifications to the code, you can install from source:

1. Clone the repository:

```bash
git clone https://github.com/samapriya/source-coop.git
cd source-coop
```

2. Install in development mode:

```bash
pip install -e .
```

## Verifying Installation

To verify that the Source Coop package is correctly installed, you can run:

```bash
source-coop --help
```

This should display the available commands and options.

You can also verify the installation within Python:

```python
import source_coop
print(source_coop.__version__)
```

## Dependencies

The Source Coop package depends on several libraries, which are automatically installed by pip:

- requests: For making HTTP requests to the Source Coop API
- boto3: For interacting with the S3-compatible storage
- rich: For nice command-line output and progress bars
- pandas and pyarrow: For data handling and exporting
- tqdm: For progress tracking
- aiohttp and aiofiles: For asynchronous downloads

These dependencies are listed in the requirements.txt file and are automatically installed by pip.

## Configuration

After installation, you need to authenticate with Source Coop before using most features. See the [Login Guide](login.md) for details on how to authenticate.

## Troubleshooting

If you encounter issues during installation:

- Make sure your Python version is 3.7 or higher
- Try upgrading pip: `pip install --upgrade pip`
- Check your internet connection
- If installing in a corporate environment, check if you need to configure a proxy

For more specific issues, please check the project's GitHub repository.
