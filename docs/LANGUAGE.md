# Macroni Language Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Language Syntax](#language-syntax)
4. [Data Types](#data-types)
5. [Operators](#operators)
6. [Control Flow](#control-flow)
7. [Functions](#functions)
8. [Built-in Functions](#built-in-functions)
9. [Template Matching Tutorial](#template-matching-tutorial)
10. [Complete Examples](#complete-examples)

---

## Introduction

Macroni is a domain-specific language designed for GUI automation, macro recording, and screen interaction. It provides built-in functions for mouse control, template matching, pixel color checking, and keyboard input simulation.

### Key Features
- Simple, readable syntax with C-style blocks
- Template matching for finding UI elements on screen
- Interactive coordinate and color capture with caching
- Mouse and keyboard control
- Recording and playback of user actions
- Pixel-perfect color checking

---

## Getting Started

### Running a Macroni Script

```bash
python macroni_interpret.py
```

### Your First Program

```macroni
# This is a comment
@print("Hello, Macroni!");

# Wait 1 second
@wait(1000);

@print("Program complete!");
```

---

## Language Syntax

### Statements
All statements must end with a semicolon (`;`).

```macroni
x = 5;
@print("Hello");
```

### Comments
Comments start with `#` and continue to the end of the line.

```macroni
# This is a comment
x = 10;  # This is also a comment
```

### Blocks
Blocks are enclosed in curly braces `{}`.

```macroni
if x > 5 {
    @print("x is greater than 5");
}
```

---

## Data Types

### Numbers
Macroni supports both integers and floating-point numbers.

```macroni
x = 42;          # Integer
y = 3.14;        # Float
z = -10;         # Negative number
```

### Strings
Strings are enclosed in double quotes.

```macroni
name = "Macroni";
message = "Hello, World!";
```

String concatenation with `+`:
```macroni
greeting = "Hello, " + "World!";
```

### null
Represents the absence of a value.

```macroni
x = null;

if x == null {
    @print("x is null");
}
```

### Tuples
Immutable ordered collections. Created with parentheses and commas.

```macroni
# Create a tuple
coords = (100, 200);
rgb = (255, 128, 0);

# Destructuring
x, y = coords;
r, g, b = rgb;

# Access by index
first = coords[0];   # 100
second = coords[1];  # 200
```

### Lists
Mutable ordered collections. Created with square brackets.

```macroni
# Create a list
numbers = [1, 2, 3, 4, 5];
empty = [];

# Access by index
first = numbers[0];  # 1

# Modify lists
@append(numbers, 6);     # Add to end
last = @pop(numbers);    # Remove from end

# Get length
count = @len(numbers);
```

---

## Operators

### Arithmetic Operators
```macroni
a = 10 + 5;      # Addition (15)
b = 10 - 5;      # Subtraction (5)
c = 10 * 5;      # Multiplication (50)
d = 10 / 5;      # Division (2)
e = 10 % 3;      # Modulo (1)
f = -10;         # Negation
```

### Comparison Operators
All comparisons return `1` (true) or `0` (false).

```macroni
x = 10;
y = 5;

a = x > y;       # Greater than (1)
b = x < y;       # Less than (0)
c = x >= y;      # Greater than or equal (1)
d = x <= y;      # Less than or equal (0)
e = x == y;      # Equal (0)
f = x != y;      # Not equal (1)
```

### Index Operator
Access elements in tuples, lists, or strings.

```macroni
numbers = [10, 20, 30];
first = numbers[0];    # 10

coords = (100, 200);
x = coords[0];         # 100
```

---

## Control Flow

### If Statements

```macroni
# Basic if
if x > 10 {
    @print("x is greater than 10");
}

# If with else
if x > 10 {
    @print("Greater");
} else {
    @print("Not greater");
}

# Nested conditions
if x > 0 {
    if x < 10 {
        @print("x is between 0 and 10");
    }
}
```

### While Loops

```macroni
# Basic while loop
counter = 0;
while counter < 5 {
    @print("Counter:", counter);
    counter = counter + 1;
}

# Infinite loop with condition
while 1 {
    @print("Running...");
    @wait(1000);

    # Break condition would go here
}
```

---

## Functions

### Defining Functions

```macroni
fn greet(name) {
    @print("Hello,", name);
}

# Call the function
greet("Alice");
```

### Functions with Return Values

Functions return the last evaluated expression.

```macroni
fn add(a, b) {
    a + b;
}

result = add(5, 3);  # result = 8
@print("Result:", result);
```

### Multiple Parameters

```macroni
fn calculate(x, y, z) {
    (x + y) * z;
}

result = calculate(2, 3, 4);  # (2 + 3) * 4 = 20
```

### Functions with Multiple Statements

```macroni
fn find_and_click(template) {
    x, y = @find_template(template);

    if x != null {
        @mouse_move(x, y, 500, 1);
        @wait(100);
        @left_click();
    } else {
        @print("Template not found:", template);
    }
}
```

---

## Built-in Functions

### Output Functions

#### @print(arg1, arg2, ...)
Prints values to the console, separated by spaces, with a newline at the end.

```macroni
@print("Hello");                    # Hello
@print("Age:", 25);                 # Age: 25
@print("RGB:", 255, 128, 0);        # RGB: 255 128 0
```

---

### Timing Functions

#### @wait(duration_ms)
#### @wait(duration_ms, random_range_ms)
#### @wait(duration_ms, min_random_ms, max_random_ms)

Pauses execution for the specified duration in milliseconds, with optional randomization.

```macroni
@wait(1000);              # Wait exactly 1 second
@wait(1000, 200);         # Wait 1000-1200ms (random)
@wait(1000, 100, 300);    # Wait 1100-1300ms (random)
```

#### @time()
Returns the current Unix timestamp (seconds since epoch).

```macroni
start = @time();
# ... do work ...
elapsed = @time() - start;
@print("Elapsed seconds:", elapsed);
```

---

### Random Functions

#### @rand(max)
#### @rand(min, max)
Returns a random float between min and max.

```macroni
x = @rand(10);        # Random float between 0 and 10
y = @rand(5, 15);     # Random float between 5 and 15
```

#### @rand_i(max)
#### @rand_i(min, max)
Returns a random integer between min and max (inclusive).

```macroni
dice = @rand_i(1, 6);     # Random integer 1-6
index = @rand_i(10);      # Random integer 0-10
```

---

### Mouse Functions

#### @mouse_move(x, y, pixels_per_second)
#### @mouse_move(x, y, pixels_per_second, human_like)

Moves the mouse to the specified coordinates.

```macroni
# Basic movement
@mouse_move(500, 300, 1000, 1);

# Fast, non-human-like movement
@mouse_move(100, 100, 5000, 0);

# Slow, human-like movement (default)
@mouse_move(800, 600, 500, 1);
```

**Parameters:**
- `x`: X coordinate
- `y`: Y coordinate
- `pixels_per_second`: Speed of movement
- `human_like`: 1 for curved path (default), 0 for straight line

#### @left_click()
Performs a left mouse click at the current position.

```macroni
@mouse_move(500, 300, 1000, 1);
@wait(100);
@left_click();
```

---

### Keyboard Functions

#### @send_input(type, key, action)
Sends keyboard or mouse input.

```macroni
@send_input("keyboard", "a", "press");
@send_input("keyboard", "a", "release");
@send_input("mouse", "left", "click");
```

**Parameters:**
- `type`: "keyboard" or "mouse"
- `key`: Key name or mouse button
- `action`: "press", "release", or "click"

#### @press_and_release(delay_ms, key1, key2, ...)
Presses multiple keys simultaneously, waits, then releases them.

```macroni
# Press and release a single key
@press_and_release(50, "a");

# Press Ctrl+C
@press_and_release(50, "ctrl", "c");

# Press Ctrl+Shift+T
@press_and_release(100, "ctrl", "shift", "t");
```

---

### Template Matching Functions

Template matching allows you to find UI elements on screen by providing reference images.

#### @set_template_dir(directory_path)
Sets the directory where template images are stored.

```macroni
@set_template_dir("./templates");
```

**Template Directory Structure:**
```
templates/
  ├── button/
  │   ├── ex1.png
  │   ├── ex2.png
  │   └── ex3.png
  ├── icon/
  │   └── ex1.png
  └── logo/
      └── ex1.png
```

The directory name is used as the template name (e.g., "button", "icon", "logo").

#### @find_template(template_name)
#### @find_template(template_name, left, top, width, height)

Finds a single instance of a template on screen. Returns `(x, y)` coordinates or `(null, null)` if not found.

```macroni
# Search entire screen
x, y = @find_template("button");

if x != null {
    @print("Found button at:", x, y);
} else {
    @print("Button not found");
}

# Search in specific region
x, y = @find_template("icon", 0, 0, 800, 600);
```

**Parameters:**
- `template_name`: Name of the template directory
- `left, top, width, height`: Optional region to search

**Returns:** `(x, y)` tuple with center coordinates, or `(null, null)`

#### @find_templates(template_name)
#### @find_templates(template_name, top_k)
#### @find_templates(template_name, left, top, width, height)
#### @find_templates(template_name, left, top, width, height, top_k)

Finds multiple instances of a template. Returns a tuple of coordinate tuples.

```macroni
# Find up to 10 matches (default)
matches = @find_templates("icon");

# Find up to 5 matches
matches = @find_templates("icon", 5);

# Find in specific region
matches = @find_templates("icon", 0, 0, 1920, 1080, 10);

# Process results
count = @len(matches);
@print("Found", count, "matches");

if count > 0 {
    first_x, first_y = matches[0];
    @print("First match at:", first_x, first_y);
}
```

**Returns:** Tuple of `(x, y)` tuples, or empty tuple `()` if none found.

---

### Coordinate Functions

#### @get_coordinates(message)
#### @get_coordinates(message, use_cache)

Interactively captures coordinates with caching support. Prompts the user to hover and press Enter.

```macroni
# First run: prompts user
x, y = @get_coordinates("Start button");

# Use cached coordinates
x, y = @get_coordinates("Start button", 1);

# Force re-capture (don't use cache)
x, y = @get_coordinates("Start button", 0);
```

**How it works:**
1. If `use_cache` is 1 and coordinates exist in cache, returns cached value
2. Otherwise, prompts user to hover mouse and press Enter
3. Captures current mouse position
4. Saves to `coordinates_cache.json` for future use

---

### Pixel Color Functions

#### @get_pixel_at(x, y)
Gets the RGB color of a pixel at specific coordinates.

```macroni
r, g, b = @get_pixel_at(500, 300);
@print("Color at (500, 300):", r, g, b);
```

**Returns:** `(r, g, b)` tuple with values 0-255

#### @get_pixel_color(alias)
#### @get_pixel_color(alias, use_cache)

Interactively captures a pixel's color with caching.

```macroni
# First run: prompts user
r, g, b = @get_pixel_color("button_active");

# Use cached color
r, g, b = @get_pixel_color("button_active", 1);
```

**How it works:**
1. If `use_cache` is 1 and color exists in cache, returns cached value
2. Otherwise, prompts user to hover over pixel and press Enter
3. Captures pixel color at mouse position
4. Saves to `pixel_colors_cache.json` for future use

#### @check_pixel_color(x, y, radius, r, g, b)
#### @check_pixel_color(x, y, radius, r, g, b, tolerance)

Checks if a specific color exists within a radius of given coordinates. Returns `1` if found, `0` otherwise.

```macroni
# Check for red pixel (255, 0, 0) within 10px of (500, 300)
found = @check_pixel_color(500, 300, 10, 255, 0, 0);

if found {
    @print("Red pixel found!");
}

# Check with tolerance (allows similar colors)
found = @check_pixel_color(500, 300, 10, 255, 0, 0, 30);
```

**Parameters:**
- `x, y`: Center point coordinates
- `radius`: Search radius in pixels
- `r, g, b`: Target color (0-255)
- `tolerance`: Optional color tolerance (default 0)

---

### Recording & Playback Functions

#### @record(recording_name)
#### @record(recording_name, start_button)
#### @record(recording_name, start_button, stop_button)

Records mouse movements, clicks, and keyboard inputs.

```macroni
# Default: space to start, esc to stop
@record("my_macro");

# Custom buttons
@record("my_macro", "f1", "f2");
```

**How it works:**
1. Displays instructions and waits for start button
2. Records all mouse/keyboard events with timestamps
3. Stops when stop button is pressed
4. Saves to `recordings_cache.json`

#### @playback(recording_name)
#### @playback(recording_name, stop_button)

Plays back a recorded session.

```macroni
@playback("my_macro");           # Default: esc to stop
@playback("my_macro", "f3");     # Custom stop button
```

**How it works:**
1. Loads recording from cache
2. Waits 3 seconds before starting
3. Replays all events at original timing
4. Can be interrupted with stop button

#### @recording_exists(recording_name)
Checks if a recording exists in the cache. Returns `1` if exists, `0` otherwise.

```macroni
if @recording_exists("my_macro") {
    @playback("my_macro");
} else {
    @print("Recording not found!");
}
```

---

### Collection Functions

#### @len(collection)
Returns the length of a tuple, list, or string.

```macroni
numbers = [1, 2, 3, 4, 5];
count = @len(numbers);     # 5

coords = (100, 200);
size = @len(coords);       # 2

text = "Hello";
length = @len(text);       # 5
```

#### @append(list, item)
Adds an item to the end of a list (modifies in place).

```macroni
numbers = [1, 2, 3];
@append(numbers, 4);
@print(@len(numbers));     # 4

coords = [];
@append(coords, (100, 200));
@append(coords, (300, 400));
```

#### @pop(list)
#### @pop(list, index)

Removes and returns an item from a list.

```macroni
numbers = [1, 2, 3, 4, 5];

# Pop from end
last = @pop(numbers);      # 5

# Pop from specific index
first = @pop(numbers, 0);  # 1

@print(@len(numbers));     # 3
```

#### @shuffle(collection)
Returns a shuffled copy of a list or tuple (original unchanged).

```macroni
numbers = [1, 2, 3, 4, 5];
shuffled = @shuffle(numbers);

# Original unchanged
@print(numbers);    # [1, 2, 3, 4, 5]
@print(shuffled);   # [3, 1, 5, 2, 4] (random)

# Works with tuples too
coords = ((10, 20), (30, 40), (50, 60));
shuffled_coords = @shuffle(coords);
```

---

## Template Matching Tutorial

### Complete Example: Finding and Clicking a Button

This tutorial shows you how to create a script that finds a button on screen and clicks it.

#### Step 1: Set Up Template Directory

Create a folder structure:
```
my_project/
  ├── script.macroni
  └── templates/
      └── login_button/
          ├── ex1.png
          ├── ex2.png
          └── ex3.png
```

#### Step 2: Capture Template Images

1. Take screenshots of the button you want to find
2. Crop them to show just the button
3. Save multiple examples (different states, lighting, etc.) in the template folder
4. Name the folder descriptively (e.g., "login_button", "play_icon", "close_button")

**Tips:**
- Include variations (normal, hover, slight position changes)
- Keep images small and focused on the distinctive part
- PNG format recommended
- The folder name becomes the template identifier

#### Step 3: Write the Script

```macroni
# Set template directory
@set_template_dir("./templates");

# Find the button
@print("Searching for login button...");
x, y = @find_template("login_button");

if x == null {
    @print("Error: Login button not found!");
} else {
    @print("Found button at:", x, y);

    # Move mouse to button
    @mouse_move(x, y, 1000, 1);

    # Wait a bit
    @wait(200, 100);

    # Click
    @left_click();

    @print("Button clicked successfully!");
}
```

#### Step 4: Advanced - Click Multiple Instances

```macroni
@set_template_dir("./templates");

# Find all instances of an icon
@print("Searching for all icons...");
matches = @find_templates("icon", 5);  # Find up to 5

count = @len(matches);
@print("Found", count, "icons");

# Click each one
i = 0;
while i < count {
    x, y = matches[i];
    @print("Clicking icon", i + 1, "at:", x, y);

    @mouse_move(x, y, 1000, 1);
    @wait(100);
    @left_click();
    @wait(500);  # Wait between clicks

    i = i + 1;
}

@print("All icons clicked!");
```

---

## Complete Examples

### Example 1: Automated Login

```macroni
@set_template_dir("./templates");

# Find and click username field
user_x, user_y = @find_template("username_field");
if user_x != null {
    @mouse_move(user_x, user_y, 1000, 1);
    @wait(100);
    @left_click();
    @wait(200);

    # Type username (simplified - use actual keyboard functions)
    @print("Type username now");
    @wait(2000);
}

# Find and click password field
pass_x, pass_y = @find_template("password_field");
if pass_x != null {
    @mouse_move(pass_x, pass_y, 1000, 1);
    @wait(100);
    @left_click();
    @wait(200);

    @print("Type password now");
    @wait(2000);
}

# Click login button
login_x, login_y = @find_template("login_button");
if login_x != null {
    @mouse_move(login_x, login_y, 1000, 1);
    @wait(100);
    @left_click();
    @print("Login clicked!");
}
```

### Example 2: Pixel Color Monitor

```macroni
# Monitor a specific pixel for color change
target_x = 500;
target_y = 300;
target_r = 255;
target_g = 0;
target_b = 0;

@print("Monitoring pixel at:", target_x, target_y);
@print("Waiting for red color...");

while 1 {
    found = @check_pixel_color(target_x, target_y, 5, target_r, target_g, target_b, 10);

    if found {
        @print("Red pixel detected!");
        # Do something
        @wait(500);
    }

    @wait(100);  # Check every 100ms
}
```

### Example 3: Random Clicking Pattern

```macroni
# Click random positions within a region
fn random_click(min_x, min_y, max_x, max_y) {
    x = @rand_i(min_x, max_x);
    y = @rand_i(min_y, max_y);

    @mouse_move(x, y, @rand_i(800, 1200), 1);
    @wait(@rand_i(100, 300));
    @left_click();
}

# Click 10 times in random locations
counter = 0;
while counter < 10 {
    random_click(100, 100, 800, 600);
    @wait(@rand_i(500, 1500));  # Random delay between clicks
    counter = counter + 1;
}

@print("Completed 10 random clicks!");
```

### Example 4: List Processing

```macroni
# Create a list of coordinates
targets = [];
@append(targets, (100, 200));
@append(targets, (300, 400));
@append(targets, (500, 600));
@append(targets, (700, 800));

@print("Total targets:", @len(targets));

# Shuffle for random order
shuffled = @shuffle(targets);

# Click each target
i = 0;
while i < @len(shuffled) {
    x, y = shuffled[i];
    @print("Target", i + 1, ":", x, y);

    @mouse_move(x, y, 1000, 1);
    @wait(100);
    @left_click();
    @wait(500);

    i = i + 1;
}
```

### Example 5: Interactive Setup with Caching

```macroni
# First run: user sets up coordinates
# Subsequent runs: uses cached values

@print("Setting up coordinates...");

# These will prompt on first run, use cache on subsequent runs
start_x, start_y = @get_coordinates("Start button", 1);
end_x, end_y = @get_coordinates("End button", 1);
target_r, target_g, target_b = @get_pixel_color("Active color", 1);

@print("Setup complete! Coordinates cached.");

# Use the coordinates
@mouse_move(start_x, start_y, 1000, 1);
@wait(100);
@left_click();

@wait(2000);

@mouse_move(end_x, end_y, 1000, 1);
@wait(100);
@left_click();

@print("Process complete!");
```

### Example 6: Record and Replay Macro

```macroni
# Record a macro
if @recording_exists("daily_routine") == 0 {
    @print("No recording found. Please record one.");
    @record("daily_routine", "space", "esc");
    @print("Recording saved!");
}

# Replay the macro 5 times
counter = 0;
while counter < 5 {
    @print("Playing macro, iteration:", counter + 1);
    @playback("daily_routine", "f4");
    @wait(2000);  # Wait between replays
    counter = counter + 1;
}

@print("All iterations complete!");
```

---

## Best Practices

### 1. Always Check for null

```macroni
x, y = @find_template("button");
if x == null {
    @print("Template not found!");
    # Handle error
} else {
    # Proceed with coordinates
}
```

### 2. Add Delays Between Actions

```macroni
@mouse_move(x, y, 1000, 1);
@wait(100, 50);  # Wait with randomization
@left_click();
```

### 3. Use Caching for Interactive Functions

```macroni
# Use 1 for use_cache to avoid re-prompting
x, y = @get_coordinates("Target", 1);
r, g, b = @get_pixel_color("Active", 1);
```

### 4. Use Descriptive Names

```macroni
# Good
login_button_x, login_button_y = @find_template("login_button");

# Bad
x1, y1 = @find_template("btn");
```

### 5. Add Randomization for Human-Like Behavior

```macroni
# Random delays
@wait(@rand_i(500, 1500));

# Random mouse speed
@mouse_move(x, y, @rand_i(800, 1200), 1);
```

### 6. Organize Templates Well

```
templates/
  ├── buttons/
  │   ├── login/
  │   ├── submit/
  │   └── cancel/
  ├── icons/
  │   ├── settings/
  │   └── profile/
  └── ui_elements/
      ├── dropdown/
      └── checkbox/
```

### 7. Use Functions for Reusable Logic

```macroni
fn find_and_click(template_name) {
    x, y = @find_template(template_name);
    if x != null {
        @mouse_move(x, y, 1000, 1);
        @wait(100);
        @left_click();
        1;  # Return success
    } else {
        0;  # Return failure
    }
}

# Use it
if find_and_click("play_button") {
    @print("Play button clicked!");
}
```

---

## Error Handling Tips

### Check Template Matching Results

```macroni
matches = @find_templates("icon", 5);
if @len(matches) == 0 {
    @print("No templates found! Check:");
    @print("1. Template directory is correct");
    @print("2. Template images exist");
    @print("3. UI element is visible on screen");
}
```

### Verify List Operations

```macroni
numbers = [1, 2, 3];
if @len(numbers) > 0 {
    item = @pop(numbers);
} else {
    @print("List is empty!");
}
```

### Check Recording Exists

```macroni
if @recording_exists("my_macro") {
    @playback("my_macro");
} else {
    @print("Recording not found. Creating new one...");
    @record("my_macro");
}
```

---

## Cache Files

Macroni creates three cache files in the working directory:

1. **coordinates_cache.json** - Stores captured coordinates from `@get_coordinates()`
2. **pixel_colors_cache.json** - Stores captured colors from `@get_pixel_color()`
3. **recordings_cache.json** - Stores recorded macros from `@record()`

These files persist between runs. To reset:
- Delete the cache files
- Use `use_cache = 0` parameter to force re-capture

---

## Summary

Macroni provides a simple yet powerful language for GUI automation. Key features:

- **Template Matching**: Find UI elements visually
- **Interactive Setup**: Capture coordinates and colors with caching
- **Mouse & Keyboard**: Full control over input
- **Recording**: Record and replay complex interactions
- **Flexible**: Lists, tuples, functions, control flow
- **Human-Like**: Randomization and curved mouse movements

Start with simple scripts and gradually build more complex automation!
