# Authenticating with Source Coop

Authentication is required for accessing certain features of Source Coop. This guide covers how to log in and manage your authentication both from the command line and programmatically.

## CLI: Logging In

To log in to Source Coop using the command-line interface:

```bash
source-coop login
```

This will prompt you for your email and password. Your credentials are securely saved as cookies in your user's config directory (`~/.config/source-coop/cookies.json` on Linux/macOS, or similar locations on other platforms) for future use.

### Optional Parameters

You can also provide your credentials directly as arguments:

```bash
source-coop login --email your.email@example.com --password yourpassword
```

!!! warning
    Providing your password directly in the command line is not recommended for security reasons, as it might be visible in your command history. The interactive prompt is more secure.

### CLI Help

For more options and help:

```bash
source-coop login --help
```

## Python SDK: Authenticating

In your Python applications, you can authenticate programmatically using the `login_to_source_coop` function:

```python
from source_coop.auth import login_to_source_coop

# Login and save cookies (will prompt for password if not provided)
cookies = login_to_source_coop(email="your.email@example.com")

# Alternatively, provide both email and password
cookies = login_to_source_coop(
    email="your.email@example.com", 
    password="yourpassword"
)

# You can also specify a custom path for saving cookies
from pathlib import Path
custom_path = Path("./my-cookies.json")
cookies = login_to_source_coop(
    email="your.email@example.com",
    save_path=custom_path
)
```

### Using Cookies with the Client

Once you have obtained cookies through login, you can use them to create an authenticated client:

```python
from source_coop import SourceCoopClient

# Create a client with the cookies from login
client = SourceCoopClient(cookies)

# Or let the client load cookies automatically from the default location
client = SourceCoopClient()  # Will use ~/.config/source-coop/cookies.json
```

### Checking Authentication Status

You can check if your client is authenticated:

```python
from source_coop import SourceCoopClient

client = SourceCoopClient()

if client.is_authenticated():
    print("Client is authenticated")
else:
    print("Client is not authenticated")
```

### Manual Cookie Management

The SDK provides functions for loading and saving cookies:

```python
from source_coop.auth import load_cookies, save_cookies

# Load cookies from the default location
cookies = load_cookies()

# Save cookies to a custom location
from pathlib import Path
custom_path = Path("./my-cookies.json")
save_cookies(cookies, custom_path)
```

## How Authentication Works

The Source Coop SDK uses cookie-based authentication. When you log in:

1. The SDK sends your credentials to Source Coop's authentication service
2. If successful, Source Coop returns session cookies
3. These cookies are saved to your filesystem for future use
4. The SDK uses these cookies for subsequent API requests

The cookies include:
- CSRF token for protection against cross-site request forgery
- Session token that authenticates your requests

## Common Issues

### Login Failures

If you encounter login failures:
- Ensure your email and password are correct
- Check your internet connection
- Verify that you can log in to the Source Coop website

### Authentication Expiration

Cookies may expire after a certain period. If your previously working code starts failing with authentication errors, try logging in again:

```bash
source-coop login
```

### Permission Issues with Cookie File

On some systems, you might encounter permission issues with the cookies file:

```bash
# Fix permissions (Linux/macOS)
chmod 600 ~/.config/source-coop/cookies.json
```

## Best Practices

- For scripts that run in automated environments, consider using environment variables for credentials
- Regularly rotate your password for security
- Be careful about sharing code that includes hardcoded credentials
- Use virtual environments to isolate authentication contexts

## Full Example

Here's a complete example of logging in and verifying authentication:

```python
from source_coop import SourceCoopClient
from source_coop.auth import login_to_source_coop

def main():
    # Try to create a client with existing cookies
    client = SourceCoopClient()
    
    # Check if we're already authenticated
    if client.is_authenticated():
        print("Already authenticated!")
    else:
        print("Not authenticated. Logging in...")
        
        # Log in and get cookies
        cookies = login_to_source_coop()
        
        if cookies:
            # Create a new client with the fresh cookies
            client = SourceCoopClient(cookies)
            print("Successfully logged in!")
        else:
            print("Login failed.")
            return
    
    # Test the authentication by getting profile info
    profile = client.api.whoami()
    if profile:
        print(f"Logged in as: {profile.get('name', 'Unknown')}")
    else:
        print("Failed to get profile information.")

if __name__ == "__main__":
    main()
```

This example demonstrates a common pattern: try to use existing credentials first, and only prompt for login if necessary.
