# Template Matching Guide

## Overview

Template matching is the core feature of Macroni that allows you to find UI elements on screen by providing reference images. This guide covers everything you need to know about setting up and using template matching effectively.

## How Template Matching Works

Template matching compares a reference image (template) against your screen to find matching locations. Macroni uses computer vision algorithms to:

1. Capture the current screen
2. Search for regions that match your template
3. Return the center coordinates of matches

## Setting Up Templates

### Directory Structure

The template directory structure is simple and hierarchical:

```
templates/
  ├── button/
  │   ├── ex1.png
  │   ├── ex2.png
  │   └── ex3.png
  ├── icon/
  │   ├── ex1.png
  │   └── ex2.png
  └── ui_element/
      ├── ex1.png
      ├── ex2.png
      ├── ex3.png
      └── ex4.png
```

**Key Points:**
- The **folder name** becomes the template identifier
- Each folder can contain multiple example images (`ex1.png`, `ex2.png`, etc.)
- Multiple examples improve match accuracy across different states/conditions

### Creating Template Images

#### Step 1: Take Screenshots

1. Navigate to the screen with your target UI element
2. Take a screenshot (Cmd+Shift+4 on macOS, Windows+Shift+S on Windows)
3. Capture the entire screen or a large region

#### Step 2: Crop the Template

1. Open the screenshot in an image editor
2. Crop to show **only the distinctive part** you want to find
3. Keep the crop tight but include enough context for uniqueness

**Good Template:**
```
┌─────────────┐
│  [ Login ]  │
└─────────────┘
```

**Bad Template (too much context):**
```
┌────────────────────────────────┐
│  Username: [____________]      │
│  Password: [____________]      │
│           [ Login ]            │
│                                │
└────────────────────────────────┘
```

#### Step 3: Save Multiple Variations

Capture the same element in different states:
- Normal state
- Hover state
- Different backgrounds
- Slight position variations
- Different zoom levels (if applicable)

Name them sequentially: `ex1.png`, `ex2.png`, `ex3.png`, etc.

### Best Practices for Template Images

1. **Size Matters**
   - Keep templates small (50-200 pixels typical)
   - Larger templates = slower matching
   - Smaller templates = more potential false matches

2. **File Format**
   - Use PNG format (supports transparency)
   - Avoid JPEG (compression artifacts reduce accuracy)

3. **Resolution**
   - Capture at the same resolution you'll run scripts on
   - Retina displays: capture at native resolution

4. **Distinctive Features**
   - Include unique visual elements (icons, text, colors)
   - Avoid generic patterns (solid colors, simple shapes)

5. **Multiple Examples**
   - 2-5 examples is usually sufficient
   - More examples = better robustness
   - Include edge cases and variations

## Using Template Matching in Scripts

### Setting the Template Directory

Always set the template directory at the start of your script:

```macroni
@set_template_dir("./templates");
```

Or use an absolute path:

```macroni
@set_template_dir("/Users/username/projects/my_automation/templates");
```

### Finding a Single Template

Use `@find_template()` to find the first match:

```macroni
x, y = @find_template("button");

if x == null {
    @print("Button not found!");
} else {
    @print("Button found at:", x, y);
}
```

**Always check for null** before using coordinates!

### Finding Multiple Templates

Use `@find_templates()` to find multiple matches:

```macroni
# Find up to 10 matches (default)
matches = @find_templates("icon");

# Find up to 5 matches
matches = @find_templates("icon", 5);

# Check results
count = @len(matches);
if count == 0 {
    @print("No icons found");
} else {
    @print("Found", count, "icons");
}
```

### Searching in a Specific Region

Limit the search area for better performance:

```macroni
# Search only top-left quadrant (0, 0, 960, 540)
x, y = @find_template("button", 0, 0, 960, 540);

# Search only bottom-right quadrant
x, y = @find_template("button", 960, 540, 960, 540);
```

**Region format:** `(left, top, width, height)`

## Complete Examples

### Example 1: Click First Match

```macroni
@set_template_dir("./templates");

fn find_and_click(template_name) {
    x, y = @find_template(template_name);

    if x == null {
        @print("Template not found:", template_name);
        0;  # Return failure
    } else {
        @print("Found", template_name, "at:", x, y);
        @mouse_move(x, y, 1000, 1);
        @wait(100);
        @left_click();
        1;  # Return success
    }
}

# Use it
if find_and_click("play_button") {
    @print("Successfully clicked play button");
}
```

### Example 2: Click All Matches

```macroni
@set_template_dir("./templates");

# Find all instances
matches = @find_templates("collect_button", 20);
count = @len(matches);

@print("Found", count, "buttons to collect");

# Click each one
i = 0;
while i < count {
    x, y = matches[i];
    @print("Collecting", i + 1, "of", count);

    @mouse_move(x, y, 1000, 1);
    @wait(100, 50);  # Random delay
    @left_click();
    @wait(500, 200);

    i = i + 1;
}

@print("Collection complete!");
```

### Example 3: Wait for Template to Appear

```macroni
@set_template_dir("./templates");

fn wait_for_template(template_name, timeout_seconds) {
    start_time = @time();
    timeout = timeout_seconds;

    @print("Waiting for", template_name, "...");

    while 1 {
        x, y = @find_template(template_name);

        if x != null {
            @print("Found", template_name, "at:", x, y);
            x, y;  # Return coordinates
        }

        # Check timeout
        elapsed = @time() - start_time;
        if elapsed > timeout {
            @print("Timeout: template not found after", timeout, "seconds");
            null, null;  # Return null
        }

        @wait(500);  # Check every 500ms
    }
}

# Use it
x, y = wait_for_template("loading_complete", 30);

if x != null {
    @print("Ready to proceed!");
}
```

### Example 4: Click Different Templates in Sequence

```macroni
@set_template_dir("./templates");

fn click_sequence(templates) {
    i = 0;
    while i < @len(templates) {
        template = templates[i];
        @print("Step", i + 1, "- Looking for:", template);

        x, y = @find_template(template);

        if x == null {
            @print("ERROR: Could not find", template);
            0;  # Return failure
        } else {
            @mouse_move(x, y, 1000, 1);
            @wait(200);
            @left_click();
            @wait(1000);  # Wait for UI to respond
        }

        i = i + 1;
    }

    1;  # Return success
}

# Define sequence
steps = ["start_button", "option_menu", "confirm_button"];

if click_sequence(steps) {
    @print("Sequence completed successfully!");
} else {
    @print("Sequence failed!");
}
```

## Troubleshooting

### Template Not Found

**Problem:** `@find_template()` returns `(null, null)`

**Solutions:**
1. **Check template directory path**
   ```macroni
   @set_template_dir("./templates");  # Verify path is correct
   ```

2. **Verify folder structure**
   - Folder name must match template name
   - At least one `ex*.png` file must exist

3. **Check UI element is visible**
   - Element must be on screen
   - Not covered by other windows
   - Not scrolled out of view

4. **Improve template quality**
   - Recapture at current resolution
   - Include more distinctive features
   - Add more variations (ex2.png, ex3.png)

5. **Try a smaller region**
   - Capture just the unique part
   - Remove surrounding context

### False Matches

**Problem:** Template matches wrong elements

**Solutions:**
1. **Make template more specific**
   - Include more unique features
   - Increase template size slightly

2. **Use region restriction**
   ```macroni
   # Only search where you expect the match
   x, y = @find_template("button", 100, 100, 800, 600);
   ```

3. **Verify with color checking**
   ```macroni
   x, y = @find_template("button");
   if x != null {
       # Verify button color
       found = @check_pixel_color(x, y, 5, 255, 0, 0, 10);
       if found {
           @print("Verified: correct button");
       }
   }
   ```

### Slow Performance

**Problem:** Template matching takes too long

**Solutions:**
1. **Reduce template size** - Smaller images = faster matching

2. **Use regions** - Search only relevant screen areas
   ```macroni
   x, y = @find_template("icon", 0, 0, 1000, 1000);
   ```

3. **Limit matches** - Don't search for more than needed
   ```macroni
   matches = @find_templates("icon", 5);  # Instead of default 10
   ```

4. **Optimize template** - Remove unnecessary details

### Resolution Issues

**Problem:** Templates don't match on different displays

**Solutions:**
1. **Capture templates on target display** - Resolution must match

2. **Create multiple template sets** - One per resolution

3. **Use resolution-independent features** - Icons/text scale better than pixel-perfect matches

## Tips for Production Use

### 1. Organize Templates by Feature

```
templates/
  ├── login/
  │   ├── username_field/
  │   ├── password_field/
  │   └── login_button/
  ├── dashboard/
  │   ├── menu_icon/
  │   └── logout_button/
  └── dialogs/
      ├── confirm_button/
      └── cancel_button/
```

### 2. Document Your Templates

Create a `templates/README.md`:

```markdown
# Template Reference

## login_button
- Used in main login screen
- Captures: Blue "Sign In" button
- Variations: Normal (ex1), hover (ex2), active (ex3)

## menu_icon
- Top-right hamburger menu
- All pages after login
```

### 3. Version Control Your Templates

```bash
git add templates/
git commit -m "Add login button templates"
```

### 4. Test on Multiple Machines

- Different screen sizes
- Different resolutions
- Different OS (if applicable)

### 5. Use Descriptive Names

```
✓ login_button/
✓ search_icon_blue/
✓ confirm_dialog_ok/

✗ btn1/
✗ icon/
✗ thing/
```

## Advanced Techniques

### Combining Template Matching with Pixel Checking

```macroni
# Find button
x, y = @find_template("submit_button");

if x != null {
    # Verify button is enabled (green color)
    r, g, b = @get_pixel_at(x, y);

    if r < 100 {
        @print("Button is enabled");
        @mouse_move(x, y, 1000, 1);
        @left_click();
    } else {
        @print("Button is disabled (red)");
    }
}
```

### Fallback Templates

```macroni
fn find_button_with_fallback() {
    # Try primary template
    x, y = @find_template("button_v2");

    if x == null {
        @print("v2 not found, trying v1...");
        x, y = @find_template("button_v1");
    }

    x, y;
}
```

### Template Validation Loop

```macroni
# Ensure template exists before proceeding
attempts = 0;
max_attempts = 5;

x, y = @find_template("critical_element");

while x == null {
    if attempts >= max_attempts {
        @print("FATAL: Element not found after", max_attempts, "attempts");
    }

    @print("Attempt", attempts + 1, "- waiting...");
    @wait(2000);

    x, y = @find_template("critical_element");
    attempts = attempts + 1;
}

@print("Element found, proceeding...");
```

## Summary

Template matching in Macroni is powerful and flexible when used correctly:

- **Create good templates** - Distinctive, appropriate size, multiple variations
- **Always check for null** - Handle "not found" cases
- **Use regions** - Improve performance and accuracy
- **Organize well** - Clear folder names and structure
- **Test thoroughly** - Multiple machines, resolutions, states

With proper setup, template matching enables robust, maintainable GUI automation!
