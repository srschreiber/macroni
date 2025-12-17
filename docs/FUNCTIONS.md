# Built-in Functions Reference

Complete reference for all Macroni built-in functions.

## Table of Contents

- [Output Functions](#output-functions)
- [Timing Functions](#timing-functions)
- [Random Functions](#random-functions)
- [Mouse Functions](#mouse-functions)
- [Keyboard Functions](#keyboard-functions)
- [Template Matching](#template-matching)
- [Coordinate Functions](#coordinate-functions)
- [Pixel Functions](#pixel-functions)
- [Recording Functions](#recording-functions)
- [Collection Functions](#collection-functions)
- [Special Functions](#special-functions)

---

## Output Functions

### @print(arg1, arg2, ...)

Prints values to the console, separated by spaces, with a newline at the end.

**Parameters:**
- `arg1, arg2, ...`: Any number of values to print

**Returns:** None

**Examples:**
```macroni
@print("Hello");                    # Hello
@print("Age:", 25);                 # Age: 25
@print("RGB:", 255, 128, 0);        # RGB: 255 128 0

x = 10;
y = 20;
@print("Coordinates:", x, y);       # Coordinates: 10 20
```

---

## Timing Functions

### @wait(duration_ms)
### @wait(duration_ms, random_range_ms)
### @wait(duration_ms, min_random_ms, max_random_ms)

Pauses execution for the specified duration in milliseconds, with optional randomization.

**Parameters:**
- `duration_ms`: Base wait time in milliseconds
- `random_range_ms`: Random 0 to N milliseconds added (optional)
- `min_random_ms`, `max_random_ms`: Random range (optional)

**Returns:** Total wait time (duration + random)

**Examples:**
```macroni
@wait(1000);              # Wait exactly 1000ms (1 second)
@wait(1000, 200);         # Wait 1000-1200ms (adds 0-200ms random)
@wait(1000, 100, 300);    # Wait 1100-1300ms (adds 100-300ms random)
@wait(500, 0, 100);       # Wait 500-600ms
```

**Use Cases:**
- Delays between actions
- Human-like timing variation
- Waiting for UI to update

---

### @time()

Returns the current Unix timestamp (seconds since epoch as a float).

**Parameters:** None

**Returns:** Float timestamp

**Examples:**
```macroni
start = @time();
@wait(1000);
elapsed = @time() - start;
@print("Elapsed seconds:", elapsed);  # Approximately 1.0

# Timeout example
start = @time();
while @time() - start < 10 {
    @print("Still running...");
    @wait(1000);
}
@print("10 seconds elapsed!");
```

---

## Random Functions

### @rand(max)
### @rand(min, max)

Returns a random floating-point number.

**Parameters:**
- `max`: Upper bound (exclusive) when used alone
- `min, max`: Range bounds

**Returns:** Float between min and max

**Examples:**
```macroni
x = @rand(10);        # Random float 0.0 to 10.0
y = @rand(5, 15);     # Random float 5.0 to 15.0
z = @rand(0, 1);      # Random float 0.0 to 1.0

# Random delay
@wait(@rand(500, 1500));

# Random position offset
offset = @rand(-10, 10);
```

---

### @rand_i(max)
### @rand_i(min, max)

Returns a random integer (inclusive on both ends).

**Parameters:**
- `max`: Upper bound (inclusive) when used alone
- `min, max`: Range bounds (both inclusive)

**Returns:** Integer between min and max (inclusive)

**Examples:**
```macroni
dice = @rand_i(1, 6);      # Random integer 1-6 (inclusive)
index = @rand_i(10);       # Random integer 0-10 (inclusive)
coin = @rand_i(0, 1);      # 0 or 1

# Random choice from 4 options
choice = @rand_i(0, 3);
if choice == 0 {
    @print("Option A");
} else if choice == 1 {
    @print("Option B");
}
# etc.
```

---

## Mouse Functions

### @mouse_move(x, y, pixels_per_second, human_like)

Moves the mouse cursor to the specified screen coordinates.

**Parameters:**
- `x`: X coordinate (pixels from left)
- `y`: Y coordinate (pixels from top)
- `pixels_per_second`: Movement speed
- `human_like`: 1 for curved/human-like path, 0 for straight line

**Returns:** 0 on success, None if coordinates are null

**Examples:**
```macroni
# Basic movement
@mouse_move(500, 300, 1000, 1);

# Fast, direct movement
@mouse_move(100, 100, 5000, 0);

# Slow, human-like movement
@mouse_move(800, 600, 500, 1);

# Random speed for realism
speed = @rand_i(800, 1200);
@mouse_move(x, y, speed, 1);

# Move to template location
x, y = @find_template("button");
if x != null {
    @mouse_move(x, y, 1000, 1);
}
```

**Notes:**
- Screen coordinates: (0, 0) is top-left
- Returns None if x or y is null (safe to use with template results)
- Human-like movement uses curved paths (more natural)

---

### @left_click()

Performs a left mouse button click at the current cursor position.

**Parameters:** None

**Returns:** 0

**Examples:**
```macroni
# Click at current position
@left_click();

# Move and click
@mouse_move(500, 300, 1000, 1);
@wait(100);  # Brief pause before clicking
@left_click();

# Double-click
@left_click();
@wait(100);
@left_click();
```

---

## Keyboard Functions

### @send_input(type, key, action)

Sends keyboard or mouse input events.

**Parameters:**
- `type`: "keyboard" or "mouse"
- `key`: Key name or button name
- `action`: "press", "release", or "click"

**Returns:** 0

**Examples:**
```macroni
# Type a letter
@send_input("keyboard", "a", "press");
@wait(50);
@send_input("keyboard", "a", "release");

# Mouse actions
@send_input("mouse", "left", "click");
@send_input("mouse", "right", "click");

# Hold shift
@send_input("keyboard", "shift", "press");
@send_input("keyboard", "a", "press");
@send_input("keyboard", "a", "release");
@send_input("keyboard", "shift", "release");
```

**Common Keys:**
- Letters: "a", "b", "c", etc.
- Modifiers: "shift", "ctrl", "alt", "cmd"
- Special: "enter", "escape", "tab", "space"

---

### @press_and_release(delay_ms, key1, key2, ...)

Presses multiple keys simultaneously, waits, then releases them in reverse order.

**Parameters:**
- `delay_ms`: How long to hold keys (milliseconds)
- `key1, key2, ...`: Keys to press

**Returns:** 0

**Examples:**
```macroni
# Single key
@press_and_release(50, "a");

# Ctrl+C (copy)
@press_and_release(50, "ctrl", "c");

# Ctrl+Shift+T (reopen tab)
@press_and_release(100, "ctrl", "shift", "t");

# Cmd+Space (Spotlight on macOS)
@press_and_release(100, "cmd", "space");

# Alt+Tab (switch windows)
@press_and_release(50, "alt", "tab");
```

**Notes:**
- Keys are pressed in order, released in reverse
- Delay applies while keys are held
- Use for keyboard shortcuts

---

## Template Matching

### @set_template_dir(directory_path)

Sets the directory where template images are stored.

**Parameters:**
- `directory_path`: Path to templates folder (string)

**Returns:** The directory path that was set

**Examples:**
```macroni
@set_template_dir("./templates");
@set_template_dir("/Users/username/automation/templates");

# Dynamic path
base = "/home/user";
@set_template_dir(base + "/templates");
```

**Directory Structure:**
```
templates/
  ├── button/
  │   ├── ex1.png
  │   └── ex2.png
  └── icon/
      └── ex1.png
```

---

### @find_template(template_name)
### @find_template(template_name, left, top, width, height)

Finds a single instance of a template on screen.

**Parameters:**
- `template_name`: Name of template folder
- `left, top, width, height`: Optional region to search

**Returns:** `(x, y)` tuple with center coordinates, or `(null, null)` if not found

**Examples:**
```macroni
# Search entire screen
x, y = @find_template("button");

if x == null {
    @print("Button not found!");
} else {
    @print("Found at:", x, y);
    @mouse_move(x, y, 1000, 1);
}

# Search specific region (top-left quadrant)
x, y = @find_template("icon", 0, 0, 960, 540);

# Search bottom-right
x, y = @find_template("icon", 960, 540, 960, 540);
```

---

### @find_templates(template_name)
### @find_templates(template_name, top_k)
### @find_templates(template_name, left, top, width, height)
### @find_templates(template_name, left, top, width, height, top_k)

Finds multiple instances of a template on screen.

**Parameters:**
- `template_name`: Name of template folder
- `top_k`: Maximum matches to find (default 10)
- `left, top, width, height`: Optional region to search

**Returns:** Tuple of `(x, y)` coordinate tuples, or empty tuple `()` if none found

**Examples:**
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
    @print("First match:", first_x, first_y);

    # Click all matches
    i = 0;
    while i < count {
        x, y = matches[i];
        @mouse_move(x, y, 1000, 1);
        @left_click();
        @wait(500);
        i = i + 1;
    }
}
```

---

## Coordinate Functions

### @get_coordinates(message, use_cache)

Interactively captures coordinates with caching.

**Parameters:**
- `message`: Label/identifier for the coordinates
- `use_cache`: 1 to use cache, 0 to force re-capture (optional)

**Returns:** `(x, y)` tuple

**Behavior:**
1. If `use_cache` is 1 and coordinates exist in `coordinates_cache.json`, returns cached value
2. Otherwise, prompts user to hover mouse and press Enter
3. Captures mouse position and saves to cache

**Examples:**
```macroni
# First run: prompts user
x, y = @get_coordinates("Start button");

# Subsequent runs: uses cache
x, y = @get_coordinates("Start button", 1);

# Force re-capture
x, y = @get_coordinates("Start button", 0);

# Multiple coordinates
play_x, play_y = @get_coordinates("Play button", 1);
pause_x, pause_y = @get_coordinates("Pause button", 1);
stop_x, stop_y = @get_coordinates("Stop button", 1);
```

**Cache File:** `coordinates_cache.json`

---

## Pixel Functions

### @get_pixel_at(x, y)

Gets the RGB color of a pixel at specific coordinates.

**Parameters:**
- `x`: X coordinate
- `y`: Y coordinate

**Returns:** `(r, g, b)` tuple with values 0-255

**Examples:**
```macroni
# Get color at specific location
r, g, b = @get_pixel_at(500, 300);
@print("Color:", r, g, b);

# Check if pixel is red
if r > 200 {
    if g < 50 {
        if b < 50 {
            @print("Pixel is red!");
        }
    }
}

# Get color at template location
x, y = @find_template("button");
if x != null {
    r, g, b = @get_pixel_at(x, y);
    @print("Button color:", r, g, b);
}
```

---

### @get_pixel_color(alias, use_cache)

Interactively captures a pixel's RGB color with caching.

**Parameters:**
- `alias`: Name/identifier for the color
- `use_cache`: 1 to use cache, 0 to force re-capture (optional)

**Returns:** `(r, g, b)` tuple

**Behavior:**
1. If `use_cache` is 1 and color exists in `pixel_colors_cache.json`, returns cached value
2. Otherwise, prompts user to hover over pixel and press Enter
3. Captures color and saves to cache

**Examples:**
```macroni
# First run: prompts user
r, g, b = @get_pixel_color("button_active");

# Subsequent runs: uses cache
r, g, b = @get_pixel_color("button_active", 1);

# Multiple colors
active_r, active_g, active_b = @get_pixel_color("active", 1);
inactive_r, inactive_g, inactive_b = @get_pixel_color("inactive", 1);
```

**Cache File:** `pixel_colors_cache.json`

---

### @check_pixel_color(x, y, radius, r, g, b, tolerance)

Checks if a specific color exists within a radius.

**Parameters:**
- `x, y`: Center point coordinates
- `radius`: Search radius in pixels
- `r, g, b`: Target RGB color (0-255)
- `tolerance`: Color tolerance, 0 = exact match (optional, default 0)

**Returns:** 1 if color found, 0 otherwise

**Examples:**
```macroni
# Check for exact red color
found = @check_pixel_color(500, 300, 10, 255, 0, 0);
if found {
    @print("Red pixel found!");
}

# Check with tolerance (finds similar reds)
found = @check_pixel_color(500, 300, 10, 255, 0, 0, 30);

# Monitor for color change
target_r = 0;
target_g = 255;
target_b = 0;

while 1 {
    found = @check_pixel_color(100, 100, 5, target_r, target_g, target_b, 10);
    if found {
        @print("Green detected!");
    }
    @wait(100);
}
```

**Use Cases:**
- Verify button state (enabled/disabled color)
- Wait for loading indicators
- Detect UI state changes
- Color-based automation triggers

---

## Recording Functions

### @record(recording_name, start_button, stop_button)

Records mouse movements, clicks, and keyboard inputs.

**Parameters:**
- `recording_name`: Identifier for the recording
- `start_button`: Button to start recording (optional, default "space")
- `stop_button`: Button to stop recording (optional, default "esc")

**Returns:** 0

**Behavior:**
1. Displays instructions
2. Waits for start button press
3. Records all mouse/keyboard events with timestamps
4. Stops when stop button is pressed
5. Saves to `recordings_cache.json`

**Examples:**
```macroni
# Default buttons (space to start, esc to stop)
@record("my_macro");

# Custom buttons
@record("login_sequence", "f1", "f2");

# Record if doesn't exist
if @recording_exists("daily_routine") == 0 {
    @print("Recording daily routine...");
    @record("daily_routine");
}
```

**Button Options:** "space", "esc", "enter", "f1"-"f12", "shift", "ctrl", "alt"

---

### @playback(recording_name, stop_button)

Plays back a recorded session.

**Parameters:**
- `recording_name`: Identifier of recording to play
- `stop_button`: Button to interrupt playback (optional, default "esc")

**Returns:** 0

**Behavior:**
1. Loads recording from `recordings_cache.json`
2. Waits 3 seconds before starting
3. Replays all events at original timing
4. Can be interrupted with stop button

**Examples:**
```macroni
# Basic playback
@playback("my_macro");

# Custom stop button
@playback("my_macro", "f4");

# Play multiple times
counter = 0;
while counter < 5 {
    @print("Replay", counter + 1);
    @playback("daily_routine");
    @wait(2000);
    counter = counter + 1;
}
```

**Error Handling:**
```macroni
if @recording_exists("my_macro") {
    @playback("my_macro");
} else {
    @print("Recording not found!");
}
```

---

### @recording_exists(recording_name)

Checks if a recording exists in the cache.

**Parameters:**
- `recording_name`: Identifier to check

**Returns:** 1 if exists, 0 otherwise

**Examples:**
```macroni
if @recording_exists("login") {
    @print("Login recording exists");
    @playback("login");
} else {
    @print("Please record login first");
    @record("login");
}

# Conditional recording
if @recording_exists("setup") == 0 {
    @print("First-time setup...");
    @record("setup");
}
```

---

## Collection Functions

### @len(collection)

Returns the length of a tuple, list, or string.

**Parameters:**
- `collection`: Tuple, list, or string

**Returns:** Integer length, or 0 if null

**Examples:**
```macroni
numbers = [1, 2, 3, 4, 5];
count = @len(numbers);     # 5

coords = (100, 200);
size = @len(coords);       # 2

text = "Hello";
length = @len(text);       # 5

# Empty collections
empty = [];
@print(@len(empty));       # 0

# Null-safe
x = null;
@print(@len(x));           # 0

# Check before accessing
matches = @find_templates("icon");
if @len(matches) > 0 {
    first_x, first_y = matches[0];
}
```

---

### @append(list, item)

Adds an item to the end of a list (modifies in place).

**Parameters:**
- `list`: List to modify
- `item`: Item to add

**Returns:** The modified list

**Examples:**
```macroni
numbers = [1, 2, 3];
@append(numbers, 4);
@print(@len(numbers));     # 4

# Build list dynamically
coords = [];
@append(coords, (100, 200));
@append(coords, (300, 400));
@append(coords, (500, 600));

# Add any type
mixed = [];
@append(mixed, 42);
@append(mixed, "hello");
@append(mixed, (10, 20));
```

**Note:** Only works with lists (not tuples, as they're immutable)

---

### @pop(list)
### @pop(list, index)

Removes and returns an item from a list.

**Parameters:**
- `list`: List to modify
- `index`: Index to remove from (optional, default = last)

**Returns:** The removed item

**Examples:**
```macroni
numbers = [1, 2, 3, 4, 5];

# Pop from end
last = @pop(numbers);      # 5
@print(@len(numbers));     # 4

# Pop from specific index
first = @pop(numbers, 0);  # 1
@print(@len(numbers));     # 3

# Pop from middle
middle = @pop(numbers, 1); # 3 (second element of remaining list)

# Process list by popping
items = [10, 20, 30, 40];
while @len(items) > 0 {
    item = @pop(items, 0);
    @print("Processing:", item);
}
```

**Error:** Raises error if list is empty or index out of range

---

### @shuffle(collection)

Returns a shuffled copy of a list or tuple (original unchanged).

**Parameters:**
- `collection`: List or tuple to shuffle

**Returns:** Shuffled copy (same type as input)

**Examples:**
```macroni
numbers = [1, 2, 3, 4, 5];
shuffled = @shuffle(numbers);

@print(numbers);    # [1, 2, 3, 4, 5] (unchanged)
@print(shuffled);   # [3, 1, 5, 2, 4] (random order)

# Shuffle tuples
coords = ((10, 20), (30, 40), (50, 60));
shuffled_coords = @shuffle(coords);

# Randomize click order
targets = @find_templates("button", 10);
random_order = @shuffle(targets);

i = 0;
while i < @len(random_order) {
    x, y = random_order[i];
    @mouse_move(x, y, 1000, 1);
    @left_click();
    @wait(500);
    i = i + 1;
}
```

---

## Special Functions

### @foreach_tick(tick_provider_func, action_func)

Repeatedly calls `action_func` while `tick_provider_func` continues.

**Parameters:**
- `tick_provider_func`: Function name that controls loop
- `action_func`: Function name to execute each iteration

**Returns:** Last return value

**Behavior:**
- Calls `tick_provider_func`, checks if it returns `EXIT_SIGNAL` (1)
- If EXIT_SIGNAL, stops loop
- Otherwise, calls `action_func`
- Repeats

**Examples:**
```macroni
fn should_continue() {
    # Return 1 to exit, anything else to continue
    x, y = @find_template("stop_button");
    if x != null {
        1;  # EXIT_SIGNAL - stop loop
    } else {
        0;  # Continue
    }
}

fn do_action() {
    @print("Running action...");
    @wait(1000);

    # Your automation logic here
    x, y = @find_template("collect");
    if x != null {
        @mouse_move(x, y, 1000, 1);
        @left_click();
    }
}

@foreach_tick(should_continue, do_action);
```

**Use Cases:**
- Run until specific condition
- Monitor-and-act loops
- Continuous automation with exit condition

---

## Summary Table

| Function | Category | Returns | Caches |
|----------|----------|---------|--------|
| @print | Output | None | No |
| @wait | Timing | Duration | No |
| @time | Timing | Timestamp | No |
| @rand | Random | Float | No |
| @rand_i | Random | Integer | No |
| @mouse_move | Mouse | 0 | No |
| @left_click | Mouse | 0 | No |
| @send_input | Keyboard | 0 | No |
| @press_and_release | Keyboard | 0 | No |
| @set_template_dir | Template | Path | No |
| @find_template | Template | (x,y) or (null,null) | No |
| @find_templates | Template | Tuple of (x,y) | No |
| @get_coordinates | Coordinate | (x,y) | Yes |
| @get_pixel_at | Pixel | (r,g,b) | No |
| @get_pixel_color | Pixel | (r,g,b) | Yes |
| @check_pixel_color | Pixel | 1 or 0 | No |
| @record | Recording | 0 | Yes |
| @playback | Recording | 0 | Reads |
| @recording_exists | Recording | 1 or 0 | Reads |
| @len | Collection | Integer | No |
| @append | Collection | List | No |
| @pop | Collection | Item | No |
| @shuffle | Collection | Collection | No |
| @foreach_tick | Special | Any | No |
