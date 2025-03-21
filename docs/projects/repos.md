# Exploring Repositories

Source Coop hosts numerous geospatial data repositories. The `repos` command helps you discover, search, and explore these repositories programmatically.

## CLI Usage

### Listing Recent Repositories

To list the most recent repositories:

```bash
source-coop repos
```

This displays a table with repository details including ID, title, account, tags, publication date, and whether the repository is featured.

### Listing Featured Repositories

To view repositories that Source Coop has highlighted as featured:

```bash
source-coop repos --featured
```

### Searching for Repositories

You can search for repositories by keyword:

```bash
source-coop repos --search "landsat"
```

This searches for repositories with "landsat" in their metadata.

### Limiting Results

By default, the command returns 10 repositories. You can adjust this limit:

```bash
source-coop repos --limit 20
```

### Pagination

For repositories with many results, you can use pagination:

```bash
# Get the first page
source-coop repos --limit 10

# Use the "next" token from the results to get the next page
source-coop repos --limit 10 --next "NEXT_TOKEN_FROM_PREVIOUS_RESULTS"
```

### Exporting Results

You can export repository data to various formats:

```bash
# Export to JSON
source-coop repos --export json --output ./repositories.json

# Export to CSV
source-coop repos --export csv --output ./repositories.csv

# Export to Parquet
source-coop repos --export parquet --output ./repositories.parquet
```

If you don't specify an output path, the file will be saved in the `./exports/` directory with a timestamped filename.

### CLI Help

For all available options:

```bash
source-coop repos --help
```

## Python SDK Usage

### Basic Repository Listing

```python
from source_coop import SourceCoopClient

def list_repositories():
    # Create a client instance
    client = SourceCoopClient()
    
    # Get a list of repositories (default limit is 10)
    repositories = client.api.get_repositories()
    
    if repositories:
        print(f"Found {repositories.get('count', 0)} repositories")
        
        # Iterate through repositories
        for repo in repositories.get('repositories', []):
            title = repo.get('meta', {}).get('title', 'Untitled')
            account = repo.get('account_id', 'Unknown')
            published = repo.get('published', 'Unknown')
            
            print(f"- {title} by {account} (Published: {published})")
        
        # Check if there are more results
        if 'next' in repositories:
            print(f"More repositories available. Next token: {repositories['next']}")
    else:
        print("Failed to fetch repositories or none found.")

if __name__ == "__main__":
    list_repositories()
```

### Featured Repositories

```python
from source_coop import SourceCoopClient

def list_featured_repositories():
    client = SourceCoopClient()
    
    # Get featured repositories
    featured = client.api.get_repositories(featured=True)
    
    if featured and featured.get('repositories'):
        print(f"Found {len(featured['repositories'])} featured repositories:")
        
        for repo in featured['repositories']:
            title = repo.get('meta', {}).get('title', 'Untitled')
            account = repo.get('account_id', 'Unknown')
            
            print(f"- {title} by {account}")
    else:
        print("No featured repositories found.")

if __name__ == "__main__":
    list_featured_repositories()
```

### Searching Repositories

```python
from source_coop import SourceCoopClient

def search_repositories(query, limit=10):
    client = SourceCoopClient()
    
    # Search for repositories
    results = client.api.get_repositories(search=query, limit=limit)
    
    if results and results.get('repositories'):
        print(f"Found {len(results['repositories'])} repositories matching '{query}':")
        
        for repo in results['repositories']:
            title = repo.get('meta', {}).get('title', 'Untitled')
            account = repo.get('account_id', 'Unknown')
            tags = ", ".join(repo.get('meta', {}).get('tags', []))
            
            print(f"- {title} by {account}")
            if tags:
                print(f"  Tags: {tags}")
    else:
        print(f"No repositories found matching '{query}'.")

if __name__ == "__main__":
    search_repositories("sentinel")
```

### Pagination Example

```python
from source_coop import SourceCoopClient

def get_all_repositories(search=None, limit_per_page=10):
    client = SourceCoopClient()
    all_repositories = []
    next_token = None
    page = 1
    
    while True:
        print(f"Fetching page {page}...")
        
        # Get a page of repositories
        result = client.api.get_repositories(
            search=search,
            limit=limit_per_page,
            next_page=next_token
        )
        
        if not result or not result.get('repositories'):
            break
        
        # Add repositories to our collection
        all_repositories.extend(result['repositories'])
        
        # Check if there are more pages
        if 'next' in result and result['next']:
            next_token = result['next']
            page += 1
        else:
            break
    
    print(f"Retrieved {len(all_repositories)} repositories in total.")
    return all_repositories

if __name__ == "__main__":
    # Get all repositories matching "landsat"
    landsat_repos = get_all_repositories(search="landsat")
    
    # Process the results
    for repo in landsat_repos:
        title = repo.get('meta', {}).get('title', 'Untitled')
        print(f"- {title}")
```

### Accessing Repository Metadata

```python
from source_coop import SourceCoopClient
import json

def examine_repository_metadata():
    client = SourceCoopClient()
    
    # Get a specific repository (by searching for a unique title)
    results = client.api.get_repositories(search="landsat", limit=1)
    
    if not results or not results.get('repositories'):
        print("No repositories found.")
        return
    
    # Get the first repository from the results
    repo = results['repositories'][0]
    
    # Basic metadata
    title = repo.get('meta', {}).get('title', 'Untitled')
    account = repo.get('account_id', 'Unknown')
    repo_id = repo.get('repository_id', 'Unknown')
    
    print(f"Repository: {title}")
    print(f"Account: {account}")
    print(f"ID: {repo_id}")
    
    # Publication details
    published = repo.get('published', 'Unknown')
    updated = repo.get('updated', 'Unknown')
    
    print(f"Published: {published}")
    print(f"Last Updated: {updated}")
    
    # Tags and description
    tags = repo.get('meta', {}).get('tags', [])
    description = repo.get('meta', {}).get('description', 'No description')
    
    print(f"Tags: {', '.join(tags)}")
    print(f"Description: {description}")
    
    # Data mode (public, etc.)
    data_mode = repo.get('data_mode', 'Unknown')
    featured = "Yes" if repo.get('featured') else "No"
    
    print(f"Data Mode: {data_mode}")
    print(f"Featured: {featured}")
    
    # Print full repository information
    print("\nFull Repository JSON:")
    print(json.dumps(repo, indent=2))

if __name__ == "__main__":
    examine_repository_metadata()
```

### Exporting Repositories to File

```python
from source_coop import SourceCoopClient
import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path

def export_repositories(export_format='json', output_path=None, search=None, limit=20):
    client = SourceCoopClient()
    
    # Get repositories
    repositories = client.api.get_repositories(search=search, limit=limit)
    
    if not repositories or not repositories.get('repositories'):
        print(f"No repositories found{' matching search' if search else ''}.")
        return None
    
    # Normalize repository data for export
    normalized_repos = []
    for repo in repositories['repositories']:
        flat_repo = {
            'repository_id': repo.get('repository_id'),
            'account_id': repo.get('account_id'),
            'title': repo.get('meta', {}).get('title'),
            'description': repo.get('meta', {}).get('description'),
            'tags': ', '.join(repo.get('meta', {}).get('tags', [])),
            'published': repo.get('published'),
            'updated': repo.get('updated'),
            'data_mode': repo.get('data_mode'),
            'featured': 'Yes' if repo.get('featured') else 'No'
        }
        normalized_repos.append(flat_repo)
    
    # Create default filename with timestamp if no output path is provided
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        search_suffix = f"-{search}" if search else ""
        filename = f"source-coop-repositories{search_suffix}-{timestamp}"
        
        export_dir = Path('exports')
        export_dir.mkdir(exist_ok=True)
        
        output_path = export_dir / filename
    else:
        output_path = Path(output_path)
    
    # Export based on format
    try:
        if export_format.lower() == 'json':
            # Export to JSON
            output_path = output_path.with_suffix('.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'repositories': normalized_repos,
                    'count': len(normalized_repos),
                    'exported_at': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
                
        elif export_format.lower() == 'csv':
            # Export to CSV
            output_path = output_path.with_suffix('.csv')
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if normalized_repos:
                    writer = csv.DictWriter(f, fieldnames=normalized_repos[0].keys())
                    writer.writeheader()
                    writer.writerows(normalized_repos)
                    
        elif export_format.lower() == 'parquet':
            # Export to Parquet
            output_path = output_path.with_suffix('.parquet')
            df = pd.DataFrame(normalized_repos)
            df.to_parquet(output_path, index=False)
            
        else:
            print(f"Unsupported export format: {export_format}")
            return None
            
        print(f"Successfully exported {len(normalized_repos)} repositories to {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"Error exporting repositories: {e}")
        return None

if __name__ == "__main__":
    # Export repositories containing "landsat" to CSV
    export_repositories(
        export_format='csv',
        output_path='./