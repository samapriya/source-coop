# Listing Organization Members

The `members` command allows you to retrieve a list of members for an organization on Source Coop. This provides insights into who belongs to an organization, their roles, and membership status.

## CLI Usage

To list members of an organization:

```bash
source-coop members ORGANIZATION_NAME
```

Replace `ORGANIZATION_NAME` with the username or account ID of the organization you want to query.

### Example Output

```
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Membership ID   ┃ Account ID   ┃ Role     ┃ State   ┃ Membership Account ID   ┃ State Changed   ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ abc123def456    │ johndoe      │ admin    │ active  │ example-org             │ 2024-02-15      │
│ ghi789jkl012    │ janedoe      │ member   │ active  │ example-org             │ 2024-02-20      │
│ mno345pqr678    │ sarahsmith   │ member   │ pending │ example-org             │ 2024-03-01      │
└────────────────┴──────────────┴──────────┴─────────┴─────────────────────────┴─────────────────┘
```

The table displays:
- Membership ID: Unique identifier for this membership
- Account ID: Username of the member
- Role: Member's role in the organization (admin, member, etc.)
- State: Membership status (active, pending, etc.)
- Membership Account ID: The organization the membership belongs to
- State Changed: When the membership state was last updated

### CLI Help

For more options and help:

```bash
source-coop members --help
```

## Python SDK Usage

### Basic Member Listing

```python
from source_coop import SourceCoopClient

def list_organization_members(organization):
    # Create a client instance
    client = SourceCoopClient()
    
    # Get members data
    members = client.api.get_members(organization)
    
    if members:
        print(f"Members of {organization}:")
        
        # Print member information
        for i, member in enumerate(members, 1):
            account_id = member.get('account_id', 'N/A')
            role = member.get('role', 'N/A')
            state = member.get('state', 'N/A')
            
            print(f"{i}. {account_id} - Role: {role}, State: {state}")
        
        return members
    else:
        print(f"Failed to get members for {organization} or no members found.")
        return None

if __name__ == "__main__":
    list_organization_members("example-org")
```

### Formatted Table Display

```python
from source_coop import SourceCoopClient
from rich.console import Console
from rich.table import Table
from rich import box

def display_members_table(organization):
    client = SourceCoopClient()
    console = Console()
    
    # Get members data
    members = client.api.get_members(organization)
    
    if not members:
        console.print(f"[red]No members found for {organization}.[/red]")
        return None
    
    # Create a rich table
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
    console.print(f"\n[bold]Members of {organization}:[/bold]")
    console.print(table)
    
    return members

if __name__ == "__main__":
    display_members_table("example-org")
```

### Filtering Members by Role

```python
from source_coop import SourceCoopClient

def get_members_by_role(organization, role):
    client = SourceCoopClient()
    
    # Get all members
    members = client.api.get_members(organization)
    
    if not members:
        print(f"Failed to get members for {organization}.")
        return []
    
    # Filter members by role
    filtered_members = [m for m in members if m.get('role') == role]
    
    print(f"Found {len(filtered_members)} members with role '{role}' in {organization}:")
    
    for member in filtered_members:
        account_id = member.get('account_id', 'N/A')
        state = member.get('state', 'N/A')
        print(f"- {account_id} (State: {state})")
    
    return filtered_members

if __name__ == "__main__":
    # Get all admins in the organization
    get_members_by_role("example-org", "admin")
```

### Finding Active vs. Pending Members

```python
from source_coop import SourceCoopClient

def analyze_membership_states(organization):
    client = SourceCoopClient()
    
    members = client.api.get_members(organization)
    
    if not members:
        print(f"Failed to get members for {organization}.")
        return None
    
    # Group members by state
    states = {}
    for member in members:
        state = member.get('state', 'unknown')
        if state not in states:
            states[state] = []
        states[state].append(member)
    
    # Print summary
    print(f"Membership states for {organization}:")
    for state, members_list in states.items():
        print(f"- {state}: {len(members_list)} members")
    
    # Print active members
    if 'active' in states:
        print("\nActive members:")
        for member in states['active']:
            account_id = member.get('account_id', 'N/A')
            role = member.get('role', 'N/A')
            print(f"- {account_id} (Role: {role})")
    
    # Print pending members
    if 'pending' in states:
        print("\nPending members:")
        for member in states['pending']:
            account_id = member.get('account_id', 'N/A')
            role = member.get('role', 'N/A')
            print(f"- {account_id} (Role: {role})")
    
    return states

if __name__ == "__main__":
    analyze_membership_states("example-org")
```

### Getting Member Details with Profiles

You can combine the members API with the profile API to get more detailed information about each member:

```python
from source_coop import SourceCoopClient
import time

def get_member_profiles(organization):
    client = SourceCoopClient()
    
    # Get members
    members = client.api.get_members(organization)
    
    if not members:
        print(f"Failed to get members for {organization}.")
        return None
    
    # Collect detailed information about each member
    member_details = []
    
    for member in members:
        account_id = member.get('account_id')
        if not account_id:
            continue
        
        print(f"Getting profile for {account_id}...")
        
        # Get profile information for this member
        profile = client.api.get_profile(account_id)
        
        # Add profile information to member data
        if profile:
            member_with_profile = {
                **member,
                'profile': {
                    'name': profile.get('name', 'N/A'),
                    'bio': profile.get('bio', 'No bio available'),
                    'account_type': profile.get('account_type', 'unknown')
                }
            }
            member_details.append(member_with_profile)
        else:
            member_details.append(member)
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Display member details
    print(f"\nDetailed member information for {organization}:")
    
    for member in member_details:
        account_id = member.get('account_id', 'N/A')
        role = member.get('role', 'N/A')
        
        # Profile information (if available)
        profile = member.get('profile', {})
        name = profile.get('name', 'Unknown')
        bio = profile.get('bio', 'No bio available')
        
        print(f"\n- {name} (@{account_id})")
        print(f"  Role: {role}")
        print(f"  Bio: {bio}")
    
    return member_details

if __name__ == "__main__":
    get_member_profiles("example-org")
```

### Finding Common Members Between Organizations

```python
from source_coop import SourceCoopClient

def find_common_members(org1, org2):
    client = SourceCoopClient()
    
    # Get members from both organizations
    members1 = client.api.get_members(org1)
    members2 = client.api.get_members(org2)
    
    if not members1 or not members2:
        print("Failed to get members for one or both organizations.")
        return []
    
    # Extract account IDs
    accounts1 = {m.get('account_id') for m in members1 if m.get('account_id')}
    accounts2 = {m.get('account_id') for m in members2 if m.get('account_id')}
    
    # Find common accounts
    common_accounts = accounts1.intersection(accounts2)
    
    print(f"Common members between {org1} and {org2}:")
    
    if common_accounts:
        for account in common_accounts:
            print(f"- {account}")
    else:
        print("No common members found.")
    
    return list(common_accounts)

if __name__ == "__main__":
    find_common_members("org-one", "org-two")
```

## Error Handling

When working with organization members, it's important to handle potential errors:

```python
from source_coop import SourceCoopClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_members_with_error_handling(organization):
    client = SourceCoopClient()
    
    try:
        # Check if we're authenticated
        if not client.is_authenticated():
            logger.warning("Not authenticated. This may affect results.")
        
        # Get profile first to confirm it's an organization
        profile = client.api.get_profile(organization)
        
        if not profile:
            logger.error(f"No profile found for {organization}.")
            return None
        
        if profile.get('account_type') != 'organization':
            logger.error(f"{organization} is not an organization. Account type: {profile.get('account_type')}")
            return None
        
        # Get members
        members = client.api.get_members(organization)
        
        if not members:
            logger.warning(f"No members found for {organization}.")
            return []
        
        logger.info(f"Successfully retrieved {len(members)} members for {organization}.")
        return members
        
    except Exception as e:
        logger.error(f"Error retrieving members for {organization}: {str(e)}")
        return None

if __name__ == "__main__":
    get_members_with_error_handling("example-org")
```

## Best Practices

1. **Check Account Type**: Before querying members, verify that the account is actually an organization.

2. **Handle Rate Limits**: When processing multiple organizations or members, consider adding delays between requests.

3. **Authentication**: Ensure you're authenticated when requesting member information, as this may be restricted for some organizations.

4. **Caching**: For applications that frequently access member information, consider implementing caching to reduce API calls.

5. **Error Recovery**: Implement proper error handling to recover from API call failures.

This members API is particularly useful for understanding organizational structures and relationships between different accounts on Source Coop.
