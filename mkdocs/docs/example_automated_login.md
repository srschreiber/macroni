# Example: Automated Login Flow

This example demonstrates automating a multi-step login process by clicking multiple UI elements in sequence.

## Features

- User-defined functions with return values
- Sequential template matching
- Error handling with conditional flow
- Human-like timing between actions

## Code

```macroni
# Example: Automated Login Flow
# Demonstrates clicking multiple UI elements in sequence

@set_template_dir("./templates");

@print("=== Automated Login Example ===");

# Helper function to find and click a template
fn find_and_click(template_name, description) {
    @print("Looking for:", description);
    x, y = @find_template(template_name);

    if x == null {
        @print("ERROR: Could not find", template_name);
        0;  # Return failure
    } else {
        @print("Found at:", x, y);
        @mouse_move(x, y, 1000, 1);
        @wait(100, 150);  # Random wait 100-150ms
        @left_click();
        @wait(300);  # Wait for UI to respond
        1;  # Return success
    }
}

# Step 1: Click username field
if find_and_click("username_field", "username field") {
    @print("Username field clicked");
    @print("[Manually type username now]");
    @wait(3000);  # Give user time to type
} else {
    @print("Login failed: username field not found");
}

# Step 2: Click password field
if find_and_click("password_field", "password field") {
    @print("Password field clicked");
    @print("[Manually type password now]");
    @wait(3000);  # Give user time to type
} else {
    @print("Login failed: password field not found");
}

# Step 3: Click login button
if find_and_click("login_button", "login button") {
    @print("Login button clicked!");
    @print("Waiting for login to complete...");
    @wait(2000);
} else {
    @print("Login failed: login button not found");
}

@print("=== Login Flow Complete ===");
```

## How to Use

1. Create template directories:
   - `templates/username_field/`
   - `templates/password_field/`
   - `templates/login_button/`
2. Add screenshots for each element
3. Run the script: `macroni automated_login.macroni`
4. Type username and password when prompted
