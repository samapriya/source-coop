# Getting Profile Information

The `profile` command allows you to retrieve detailed information about a user or organization on Source Coop. This information includes account details, bio, and other public profile data.

## CLI Usage

To get profile information for a user or organization:

```bash
source-coop profile USERNAME
```

Replace `USERNAME` with the username or account ID of the user or organization you want to look up.

### Example Output

When retrieving a user profile, you'll see general account information:

```
User Profile: johndoe

{
  "account_id": "johndoe",
  "account_type": "user",
  "name": "John Doe",
  "bio": "GIS specialist working with satellite imagery",
  "email": "john.doe@example.com",
  ...
}
```

When retrieving an organization profile, you'll see organization details and members:

```
Organization Profile: acme-corp

Name: ACME Corporation
Bio: Provider of geospatial data products

Organization Members:
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Membership ID   ┃ Account ID   ┃ Role     ┃ State   ┃ Membership Account ID   ┃ State Changed   ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ abcd1234       │ johndoe      │ admin    │ active  │ acme-corp               │ 2024-12-01      │
│ efgh5678       │ janedoe      │ member   │ active  │ acme-corp               │ 2024-12-05      │
└────────────────┴──────────────┴──────────┴─────────┴──────────────────────────┴─────────────────┘
```

### CLI Help

For more options and help:

```bash
source-coop profile --help
```

## Python SDK Usage

### Getting a User Profile

```python
from source_coop import SourceCoopClient
import json

def get_user_profile(username):
    # Create a client instance
    client = SourceCoopClient()
    
    # Get profile information
    profile = client.api.get_profile(username)
    
    if profile:
        print(f"Profile information for {username}:")
        
        # Pretty print the profile data
        print(json.dumps(profile, indent=2))
        
        # Get specific data fields
        account_type = profile.get('account_type', 'unknown')
        name = profile.get('name', 'N/A')
        bio = profile.get('bio', 'No bio available')
        
        print(f"\nAccount Type: {account_type}")
        print(f"Name: {name}")
        print(f"Bio: {bio}")
        
        return profile
    else:
        print(f"Failed to get profile for {username}.")
        return None

if __name__ == "__main__":
    get_user_profile("johndoe")
```

### Getting an Organization Profile

```python
from source_coop import SourceCoopClient
import json

def get_organization_profile(org_name):
    client = SourceCoopClient()
    
    # Get profile information
    profile = client.api.get_profile(org_name)
    
    if not profile:
        print(f"Failed to get profile for {org_name}.")
        return None
    
    # Check if this is an organization
    if profile.get('account_type') != 'organization':
        print(f"{org_name} is not an organization. Account type: {profile.get('account_type')}")
        return profile
    
    print(f"Organization Profile: {org_name}")
    print(f"Name: {profile.get('name', 'N/A')}")
    print(f"Bio: {profile.get('bio', 'No bio available')}")
    
    # Get organization members
    members = client.api.get_members(org_name)
    
    if members:
        print(f"\nOrganization Members ({len(members)}):")
        for member in members:
            member_id = member.get('account_id', 'N/A')
            role = member.get('role', 'N/A')
            state = member.get('state', 'N/A')
            print(f"- {member_id} ({role}, {state})")
    else:
        print("\nFailed to get organization members or none found.")
    
    return profile

if __name__ == "__main__":
    get_organization_profile("example-org")
```

### Checking If an Account is a User or Organization

```python
from source_coop import SourceCoopClient

def check_account_type(account_id):
    client = SourceCoopClient()
    
    profile = client.api.get_profile(account_id)
    
    if not profile:
        print(f"Could not find account: {account_id}")
        return None
    
    account_type = profile.get('account_type')
    
    if account_type == 'user':
        print(f"{account_id} is a user account.")
        # Process user-specific data...
    elif account_type == 'organization':
        print(f"{account_id} is an organization account.")
        # Process organization-specific data...
    else:
        print(f"{account_id} has an unknown account type: {account_type}")
    
    return account_type

if __name__ == "__main__":
    check_account_type("example-account")
```

## Getting Profile and Members in One Call

For organization accounts, you may want to retrieve both the profile and members in a single function:

```python
from source_coop import SourceCoopClient
from rich.console import Console
from rich.table import Table
from rich import box

def get_org_with_members(org_name):
    client = SourceCoopClient()
    console = Console()
    
    # Get profile information
    profile = client.api.get_profile(org_name)
    
    if not profile:
        console.print(f"[red]Failed to get profile for {org_name}.[/red]")
        return None
    
    if profile.get('account_type') != 'organization':
        console.print(f"[yellow]{org_name} is not an organization.[/yellow]")
        return profile
    
    # Display organization info
    console.print(f"\n[bold green]Organization Profile:[/bold green] {org_name}")
    console.print(f"[bold]Name:[/bold] {profile.get('name', 'N/A')}")
    console.print(f"[bold]Bio:[/bold] {profile.get('bio', 'N/A')}")
    
    # Get and display members
    members = client.api.get_members(org_name)
    
    if not members:
        console.print("[yellow]No members data available[/yellow]")
        return profile
    
    # Create a rich table for members
    table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
    
    # Add columns
    table.add_column("Membership ID", style="cyan")
    table.add_column("Account ID", style="green")
    table.add_column("Role", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("Membership Account ID", style="blue")
    table.add_column("State Changed", style="bright_cyan")
    
    # Add rows
    for member in members:
        table.add_row(
            member.get('membership_id', 'N/A'),
            member.get('account_id', 'N/A'),
            member.get('role', 'N/A'),
            member.get('state', 'N/A'),
            member.get('membership_account_id', 'N/A'),
            member.get('state_changed', 'N/A')
        )
    
    # Print the table
    console.print("\n[bold]Organization Members:[/bold]")
    console.print(table)
    
    return {
        'profile': profile,
        'members': members
    }

if __name__ == "__main__":
    get_org_with_members("example-org")
```

## Error Handling

When working with profile data, it's important to handle potential errors:

```python
from source_coop import SourceCoopClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_profile_with_error_handling(account_id):
    client = SourceCoopClient()
    
    try:
        # Check authentication first
        if not client.is_authenticated():
            logger.warning("Not authenticated. Some profile information may be restricted.")
        
        # Get profile data
        profile = client.api.get_profile(account_id)
        
        if not profile:
            logger.error(f"No profile found for {account_id}.")
            return None
        
        logger.info(f"Successfully retrieved profile for {account_id}.")
        return profile
        
    except Exception as e:
        logger.error(f"Error retrieving profile for {account_id}: {str(e)}")
        return None

if __name__ == "__main__":
    get_profile_with_error_handling("example-account")
```

## Combining with Repository Information

You can combine profile information with repository data for a complete view of an account:

```python
from source_coop import SourceCoopClient
from source_coop.s3 import SourceCoopS3

def get_account_overview(account_id):
    client = SourceCoopClient()
    
    # Get profile information
    profile = client.api.get_profile(account_id)
    
    if not profile:
        print(f"Failed to get profile for {account_id}.")
        return None
    
    print(f"Account: {account_id}")
    print(f"Name: {profile.get('name', 'N/A')}")
    print(f"Type: {profile.get('account_type', 'N/A')}")
    print(f"Bio: {profile.get('bio', 'No bio available')}")
    
    # Get repositories for this account
    # Note: We search for repositories using the account ID
    print("\nSearching for repositories...")
    repositories = client.api.get_repositories(search=account_id)
    
    if repositories and repositories.get('repositories'):
        repos = repositories['repositories']
        print(f"\nFound {len(repos)} repositories:")
        
        for repo in repos:
            # Filter to only include repos owned by this account
            if repo.get('account_id') == account_id:
                title = repo.get('meta', {}).get('title', 'Untitled')
                description = repo.get('meta', {}).get('description', 'No description')
                published = repo.get('published', 'Unknown date')
                
                print(f"\n- {title}")
                print(f"  Published: {published}")
                print(f"  Description: {description}")
                
                # Generate S3 URL for this repository
                repo_id = repo.get('repository_id', '')
                if repo_id:
                    s3_url = f"s3://{account_id}/{repo_id}"
                    print(f"  S3 URL: {s3_url}")
    else:
        print("\nNo repositories found for this account.")
    
    return {
        'profile': profile,
        'repositories': repositories.get('repositories', []) if repositories else []
    }

if __name__ == "__main__":
    get_account_overview("example-account")
```

This comprehensive example shows how to combine profile information with repository data to create a complete overview of an account.
