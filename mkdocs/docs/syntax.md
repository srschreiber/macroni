# Language Syntax

Complete guide to Macroni language syntax and features.

## Basic Syntax

### Comments

```macroni
# Single-line comments start with #
x = 10;  # Inline comments are supported
```

### Statements

All statements end with a semicolon `;`

```macroni
x = 10;
name = "test";
@print("Hello");
```

---

## Data Types

### Primitives

```macroni
# Integers
x = 42;
y = -10;

# Floats
pi = 3.14159;
temp = -273.15;

# Strings (double quotes only)
name = "Alice";
message = "Hello, world!";

# Booleans
enabled = true;   # true = 1
disabled = false; # false = 0

# Null
value = null;
```

### Collections

#### Tuples (Immutable)

```macroni
# Create tuples with parentheses
coords = (100, 200);
rgb = (255, 128, 0);
empty = ();

# Destructuring
x, y = (100, 200);
r, g, b = rgb;

# Indexing
first = coords[0];  # 100
second = coords[1]; # 200
```

!!! note
    Tuples are immutable - you cannot modify elements after creation.

#### Lists (Mutable)

```macroni
# Create lists with square brackets
items = [1, 2, 3, 4];
names = ["Alice", "Bob", "Charlie"];
mixed = [1, "two", 3.0, true];
empty = [];

# Indexing
first = items[0];      # 1
last = items[3];       # 4

# Modify elements
items[0] = 10;         # items is now [10, 2, 3, 4]

# List operations
@append(items, 5);     # Add to end
popped = @pop(items);  # Remove from end
```

---

## Variables

### Assignment

```macroni
# Single assignment
x = 10;
name = "test";

# Multiple assignment (destructuring)
x, y = (100, 200);
a, b, c = [1, 2, 3];

# From function returns
text, conf, bbox = @ocr_find_text(region, 0.8, null, 1.0)[0];
```

### Scope

```macroni
x = 10;  # Global variable

fn my_function() {
    y = 20;     # Local to function
    outer x;    # Declare x as outer scope
    x = 15;     # Modifies global x
}

my_function();
@print(x);  # 15
# @print(y);  # Error: y is not defined
```

!!! tip "Outer Variables"
    Use `outer` keyword to modify variables from enclosing scope.

---

## Operators

### Arithmetic

```macroni
a = 10 + 5;   # Addition: 15
b = 10 - 5;   # Subtraction: 5
c = 10 * 5;   # Multiplication: 50
d = 10 / 5;   # Division: 2
e = 10 % 3;   # Modulo: 1
f = -x;       # Negation
```

### Comparison

```macroni
a = x > 10;   # Greater than
b = x < 10;   # Less than
c = x >= 10;  # Greater than or equal
d = x <= 10;  # Less than or equal
e = x == 10;  # Equal
f = x != 10;  # Not equal
```

### Logical

```macroni
# AND (&&)
if x > 5 && y < 10 {
    @print("Both conditions true");
}

# OR (||)
if x == 0 || y == 0 {
    @print("At least one is zero");
}

# NOT (!)
if !enabled {
    @print("Disabled");
}
```

### Indexing

```macroni
# Lists and tuples
items = [10, 20, 30];
first = items[0];      # 10
last = items[2];       # 30

# Nested indexing
matrix = [[1, 2], [3, 4]];
value = matrix[0][1];  # 2

# String indexing (not supported directly, use @str operations)
```

---

## Control Flow

### If Statements

```macroni
# Simple if
if x > 10 {
    @print("Greater than 10");
}

# If-else
if x > 10 {
    @print("Greater");
} else {
    @print("Not greater");
}

# Nested conditions
if x > 0 {
    if x < 10 {
        @print("Between 0 and 10");
    } else {
        @print("10 or more");
    }
} else {
    @print("Zero or negative");
}

# Inline conditional (expression)
result = if x > 0 { 1 } else { -1 };
```

### While Loops

```macroni
# Basic while loop
x = 0;
while x < 10 {
    @print(x);
    x = x + 1;
}

# Infinite loop with break
while true {
    x = x + 1;
    if x > 100 {
        break;  # Exit loop
    }
}

# Continue statement
x = 0;
while x < 10 {
    x = x + 1;
    if x % 2 == 0 {
        continue;  # Skip even numbers
    }
    @print(x);
}
```

!!! note "No For Loops"
    Macroni uses `while` loops exclusively. Iterate over collections using indices and `@len()`.

    ```macroni
    items = [1, 2, 3, 4];
    i = 0;
    while i < @len(items) {
        @print(items[i]);
        i = i + 1;
    }
    ```

---

## Functions

### Function Definition

```macroni
# Simple function
fn greet() {
    @print("Hello!");
}

# Function with parameters
fn add(a, b) {
    return a + b;
}

# Multiple parameters
fn move_and_click(x, y, speed) {
    @mouse_move(x, y, speed, true);
    @left_click();
}
```

### Return Values

```macroni
# Single return value
fn square(x) {
    return x * x;
}

# Multiple return values (tuple)
fn get_bounds() {
    return (0, 0, 1920, 1080);
}

x1, y1, x2, y2 = get_bounds();

# No return (implicit null)
fn log_message(msg) {
    @print("[LOG]", msg);
    # No return statement
}
```

### Function Calls

```macroni
# No arguments
greet();

# With arguments
result = add(10, 20);
move_and_click(500, 300, 1000);

# Nested calls
result = add(square(3), square(4));  # 9 + 16 = 25

# Built-in functions (prefixed with @)
@print("Hello");
@wait(1000);
region = @capture_region("area", false);
```

---

## Built-in Functions

All built-in functions start with `@` symbol.

### Categories

- **OCR:** `@capture_region()`, `@ocr_find_text()`
- **Mouse:** `@mouse_move()`, `@left_click()`, `@mouse_position()`
- **Keyboard:** `@press_and_release()`, `@send_input()`
- **Screen:** `@get_coordinates()`, `@get_pixel_at()`, `@check_pixel_color()`
- **Template Matching:** `@set_template_dir()`, `@find_template()`, `@find_templates()`
- **Timing:** `@wait()`, `@time()`
- **Random:** `@rand()`, `@rand_i()`
- **Recording:** `@record()`, `@playback()`, `@recording_exists()`
- **Lists:** `@len()`, `@append()`, `@pop()`, `@shuffle()`, `@swap()`, `@copy()`
- **Type Checking:** `@is_int()`, `@is_float()`, `@is_str()`, `@is_list()`, `@is_tuple()`
- **Type Conversion:** `@int()`, `@float()`, `@str()`
- **Utility:** `@print()`

See [Function Reference](functions.md) for complete documentation.

---

## Modules

### Importing

```macroni
import "utils.macroni";
import "helpers/mouse.macroni";
```

!!! note
    - Import paths are relative to the current file
    - Use `.macroni` file extension
    - Imports must appear at the top of the file

---

## Common Patterns

### OCR Text Finding

```macroni
# Recommended approach for UI automation
fn find_and_click(text) {
    region = @capture_region("search_area", false);
    results = @ocr_find_text(region, 0.8, text, 1.0);

    if @len(results) > 0 {
        txt, conf, bbox = results[0];
        x, y = bbox[0];  # Top-left corner
        @mouse_move(x, y, 500, true);
        @left_click();
        return true;
    }
    return false;
}
```

### Template Matching

```macroni
fn click_template(name) {
    x, y = @find_template(name);
    if x != null {
        @mouse_move(x, y, 1000, true);
        @left_click();
        return true;
    }
    return false;
}
```

### Color-based Waiting

```macroni
fn wait_for_color(x, y, r, g, b, timeout_ms) {
    start = @time();
    while true {
        if @check_pixel_color(x, y, 5, r, g, b, 10) {
            return true;
        }

        elapsed = @time() - start;
        if elapsed * 1000 > timeout_ms {
            return false;  # Timeout
        }

        @wait(100);
    }
}
```

### List Iteration

```macroni
items = [100, 200, 300, 400];
i = 0;
while i < @len(items) {
    @print("Item", i, "=", items[i]);
    i = i + 1;
}
```

### Retry Logic

```macroni
fn retry(max_attempts) {
    attempts = 0;
    while attempts < max_attempts {
        x, y = @find_template("button");
        if x != null {
            @mouse_move(x, y, 500, true);
            @left_click();
            return true;
        }
        attempts = attempts + 1;
        @wait(500);
    }
    return false;  # Failed after all attempts
}
```

---

## Cache Files

Macroni automatically creates cache files in your working directory:

| File | Purpose | Functions |
|------|---------|-----------|
| `regions_cache.json` | OCR regions | `@capture_region()` |
| `coordinates_cache.json` | Screen coordinates | `@get_coordinates()` |
| `pixel_colors_cache.json` | Pixel colors | `@get_pixel_color()` |
| `recordings_cache.json` | Macro recordings | `@record()`, `@playback()` |

!!! tip "Cache Management"
    - Delete cache files to reset all saved values
    - Use `overwrite_cache` / `use_cache` parameters to control caching per call
    - Caches are key-value stores - changing the key creates a new entry

---

## Best Practices

!!! success "Do"
    - Use descriptive variable and function names
    - Cache regions with `@capture_region()` for consistent OCR
    - Add randomness to timing with `@wait(min, max)` for human-like behavior
    - Use `@len()` to safely check collection sizes before indexing
    - Break complex logic into small functions
    - Use `human_like=true` in `@mouse_move()` for natural movement

!!! failure "Don't"
    - Mix tabs and spaces (choose one)
    - Forget semicolons at statement ends
    - Modify tuples (they're immutable)
    - Use undefined variables (no implicit declarations)
    - Create infinite loops without break conditions
    - Index beyond list/tuple bounds (check `@len()` first)
