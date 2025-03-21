# Checking Authentication Status

The `whoami` command allows you to check your current authentication status and display information about the logged-in user. This is useful for verifying that you're properly authenticated before performing operations that require authentication.

## CLI Usage

To check who you're currently logged in as:

```bash
source-coop whoami
```

### Example Output

When authenticated:

```
Logged in as: John Doe
```

When not authenticated:

```
Not logged in. Use 'login' command first.
```

### CLI Help

For help with the command:

```bash
source-coop whoami --help
```

## Python SDK Usage

In your Python scripts, you can check authentication status and retrieve profile information using the SDK:

```python
from source_coop import SourceCoopClient

def check_authentication():
    # Create a client instance
    client = SourceCoopClient()
    
    # Check if the client has valid authentication cookies
    if not client.is_authenticated():
        print("Not authenticated. Please run 'source-coop login' first.")
        return None
    
    # Get the profile information for the authenticated user
    profile = client.api.whoami()
    
    if profile:
        print(f"Logged in as: {profile.get('name', 'Unknown')}")
        return profile
    else:
        print("Failed to get user profile. You may need to log in again.")
        return None

if __name__ == "__main__":
    check_authentication()
```

### Checking Authentication Without Printing

If you just want to check authentication status within your code without printing messages:

```python
from source_coop import SourceCoopClient

def is_authenticated():
    client = SourceCoopClient()
    
    # First check if we have authentication cookies
    if not client.is_authenticated():
        return False
    
    # Then verify the cookies are still valid by making an API call
    profile = client.api.whoami()
    return profile is not None

if __name__ == "__main__":
    if is_authenticated():
        # Proceed with authenticated operations
        print("Authentication is valid")
    else:
        # Handle unauthenticated state
        print("Authentication is not valid")
```

### Getting Profile Details

The profile information returned by `whoami()` contains details about the authenticated user:

```python
from source_coop import SourceCoopClient
import json

def get_profile_details():
    client = SourceCoopClient()
    
    if not client.is_authenticated():
        print("Not authenticated.")
        return None
    
    profile = client.api.whoami()
    
    if profile:
        # Print entire profile as formatted JSON
        print(json.dumps(profile, indent=2))
        
        # Access specific fields
        print(f"Name: {profile.get('name')}")
        print(f"Email: {profile.get('email')}")
        # Other fields depend on the Source Coop API response
        
        return profile
    else:
        print("Failed to get profile information.")
        return None

if __name__ == "__main__":
    get_profile_details()
```

## Integrating with Other Operations

The `whoami` functionality is often used to check authentication before performing other operations:

```python
from source_coop import SourceCoopClient

def main():
    client = SourceCoopClient()
    
    # Check authentication
    if not client.is_authenticated():
        print("Not authenticated. Please run 'source-coop login' first.")
        return
    
    profile = client.api.whoami()
    if not profile:
        print("Failed to get user profile. You may need to log in again.")
        return
    
    print(f"Logged in as: {profile.get('name', 'Unknown')}")
    
    # Continue with other operations now that we know we're authenticated
    print("Listing repositories...")
    repos = client.api.get_repositories(limit=5)
    
    if repos:
        print(f"Found {repos.get('count', 0)} repositories")
        # Process repositories...
    else:
        print("Failed to list repositories.")

if __name__ == "__main__":
    main()
```

## Error Handling

When working with authentication checks, it's important to handle potential errors:

```python
from source_coop import SourceCoopClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_auth_with_error_handling():
    try:
        client = SourceCoopClient()
        
        if not client.is_authenticated():
            logger.warning("Not authenticated. Please log in first.")
            return False
        
        profile = client.api.whoami()
        
        if not profile:
            logger.warning("Authentication may have expired. Please log in again.")
            return False
        
        logger.info(f"Authenticated as: {profile.get('name', 'Unknown')}")
        return True
        
    except Exception as e:
        logger.error(f"Error checking authentication: {str(e)}")
        return False

if __name__ == "__main__":
    check_auth_with_error_handling()
```

## Best Practices

1. **Check Authentication Early**: Verify authentication at the beginning of your scripts to fail fast if there's an issue.

2. **Handle Expired Sessions**: Remember that sessions can expire, so check authentication before important operations even if you've already checked it earlier.

3. **Clear Error Messages**: Provide clear guidance to users when authentication fails, such as suggesting to run the login command.

4. **Automatic Login**: For better user experience in interactive scripts, you can automatically prompt for login if authentication fails:

```python
from source_coop import SourceCoopClient
from source_coop.auth import login_to_source_coop

def ensure_authenticated():
    client = SourceCoopClient()
    
    # Try with existing cookies first
    if client.is_authenticated() and client.api.whoami():
        return client
    
    print("Authentication required. Please log in.")
    
    # Prompt for login
    cookies = login_to_source_coop()
    
    if cookies:
        # Create a new client with fresh cookies
        return SourceCoopClient(cookies)
    else:
        print("Login failed.")
        return None

if __name__ == "__main__":
    client = ensure_authenticated()
    if client:
        print("Successfully authenticated!")
        # Continue with authenticated operations...
    else:
        print("Could not authenticate.")
```

This pattern provides a smooth user experience in interactive environments by automatically handling login when needed.
