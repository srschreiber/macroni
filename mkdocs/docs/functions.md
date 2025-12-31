# Function Reference

Complete reference for all built-in Macroni functions.

## OCR Functions

### `@capture_region(key, overwrite_cache)`

Interactive region capture with caching.

**Parameters:**

- `key` (string): Unique identifier for caching
- `overwrite_cache` (boolean): `true` to force recapture, `false` to use cache

**Returns:** `(x1, y1, x2, y2)` - Top-left and bottom-right coordinates

**Cache:** Saved to `regions_cache.json`

!!! example
    ```macroni
    region = @capture_region("search_box", false);  # Use cache
    region = @capture_region("search_box", true);   # Force recapture
    ```

!!! note "Interactive Flow"
    1. Hover mouse over top-left corner → Press Enter
    2. Hover mouse over bottom-right corner → Press Enter

---

### `@ocr_find_text(region, min_conf, filter, upscale)`

Find text on screen using OCR (EasyOCR).

**Parameters:**

- `region` (tuple or null): `(x1, y1, x2, y2)` from `@capture_region()` or `null` for full screen
- `min_conf` (float): Confidence threshold 0.0-1.0 (0.8 recommended)
- `filter` (string or null): Case-insensitive substring to search for, or `null` for all text
- `upscale` (float): Scaling factor - `1.0` = default, `0.5` = faster, `2.0` = tiny text

**Returns:** List of `(text, confidence, [[x1,y1], [x2,y2], [x3,y3], [x4,y4]])`

- Bounding box has 4 corners in screen coordinates
- Sorted by confidence (highest first)

!!! example
    ```macroni
    results = @ocr_find_text(region, 0.8, "Login", 1.0);
    if @len(results) > 0 {
        text, conf, bbox = results[0];
        x, y = bbox[0];  # Top-left corner
        @mouse_move(x, y, 500, true);
        @left_click();
    }
    ```

!!! tip "GPU Acceleration"
    Edit `ocr.py` line 10: `reader = easyocr.Reader(['en'], gpu=True)` (Requires CUDA)

---

## Mouse Functions

### `@mouse_move(x, y, speed, human_like)`

Move mouse cursor to coordinates.

**Parameters:**

- `x` (int): X coordinate
- `y` (int): Y coordinate
- `speed` (int): Movement speed in pixels/second
- `human_like` (boolean): `true` for curved path, `false` for straight line

**Returns:** None

!!! example
    ```macroni
    @mouse_move(500, 300, 1000, true);  # Smooth, human-like movement
    ```

---

### `@left_click()`

Perform left mouse click at current cursor position.

**Parameters:** None

**Returns:** None

!!! example
    ```macroni
    @mouse_move(100, 200, 500, true);
    @left_click();
    ```

---

### `@mouse_position()`

Get current mouse cursor position.

**Parameters:** None

**Returns:** `(x, y)` - Current cursor coordinates

!!! example
    ```macroni
    x, y = @mouse_position();
    @print("Cursor at:", x, y);
    ```

---

## Keyboard Functions

### `@press_and_release(delay_ms, ...keys)`

Press and release keyboard keys in sequence.

**Parameters:**

- `delay_ms` (int): Delay between press and release in milliseconds
- `...keys` (strings): Variable number of key names (e.g., "ctrl", "c", "shift", "a")

**Returns:** None

!!! example
    ```macroni
    @press_and_release(50, "ctrl", "c");       # Copy
    @press_and_release(50, "ctrl", "v");       # Paste
    @press_and_release(100, "ctrl", "alt", "delete");
    ```

---

### `@send_input(type, key, action)`

Low-level input control.

**Parameters:**

- `type` (string): `"keyboard"` or `"mouse"`
- `key` (string): Key or button name
- `action` (string): `"press"`, `"release"`, or `"click"`

**Returns:** None

!!! example
    ```macroni
    @send_input("keyboard", "a", "press");
    @wait(100);
    @send_input("keyboard", "a", "release");
    ```

---

## Template Matching

### `@set_template_dir(path)`

Set directory containing template images.

**Parameters:**

- `path` (string): Path to templates directory

**Returns:** None

!!! note "Directory Structure"
    ```
    templates/
    ├── button/
    │   ├── ex1.png
    │   └── ex2.png
    └── icon/
        └── ex1.png
    ```

!!! example
    ```macroni
    @set_template_dir("./templates");
    ```

---

### `@find_template(name)` / `@find_template(name, left, top, width, height)`

Find first template match on screen.

**Parameters:**

- `name` (string): Template name (subdirectory in templates folder)
- `left, top, width, height` (optional ints): Search region bounds

**Returns:** `(x, y)` coordinates of center, or `(null, null)` if not found

!!! example
    ```macroni
    x, y = @find_template("button");
    if x != null {
        @mouse_move(x, y, 1000, true);
        @left_click();
    }

    # Search in specific region
    x, y = @find_template("icon", 0, 0, 1920, 1080);
    ```

---

### `@find_templates(name, top_k)`

Find multiple template matches.

**Parameters:**

- `name` (string): Template name
- `top_k` (int): Maximum number of matches to return

**Returns:** Tuple of `(x, y)` coordinate pairs

!!! example
    ```macroni
    matches = @find_templates("button", 5);
    x, y = matches[0];  # First match
    ```

---

## Screen Functions

### `@get_coordinates(label, use_cache)`

Interactive coordinate capture.

**Parameters:**

- `label` (string): Unique identifier for caching
- `use_cache` (boolean): `true` to use cache, `false` to recapture

**Returns:** `(x, y)` coordinates

**Cache:** Saved to `coordinates_cache.json`

!!! example
    ```macroni
    x, y = @get_coordinates("login_button", true);
    @mouse_move(x, y, 500, true);
    ```

---

### `@get_pixel_at(x, y)`

Get RGB color at specific pixel.

**Parameters:**

- `x` (int): X coordinate
- `y` (int): Y coordinate

**Returns:** `(r, g, b)` - RGB values (0-255)

!!! example
    ```macroni
    r, g, b = @get_pixel_at(100, 200);
    @print("Color:", r, g, b);
    ```

---

### `@get_pixel_color(alias, use_cache)`

Interactive color capture.

**Parameters:**

- `alias` (string): Unique identifier for caching
- `use_cache` (boolean): `true` to use cache, `false` to recapture

**Returns:** `(r, g, b)` - RGB values

**Cache:** Saved to `pixel_colors_cache.json`

!!! example
    ```macroni
    r, g, b = @get_pixel_color("button_color", true);
    ```

---

### `@check_pixel_color(x, y, radius, r, g, b, tolerance)`

Check if pixel color matches within tolerance.

**Parameters:**

- `x, y` (int): Coordinates
- `radius` (int): Search radius in pixels
- `r, g, b` (int): Expected RGB values (0-255)
- `tolerance` (int): Color difference tolerance (0-255)

**Returns:** `true` if match found, `false` otherwise

!!! example
    ```macroni
    found = @check_pixel_color(100, 200, 5, 255, 0, 0, 10);
    if found {
        @print("Red pixel found!");
    }
    ```

---

## Timing Functions

### `@wait(ms)` / `@wait(ms, random_min, random_max)`

Pause execution.

**Parameters:**

- `ms` (int): Base wait time in milliseconds
- `random_min, random_max` (optional ints): Random delay range to add

**Returns:** None

!!! example
    ```macroni
    @wait(1000);              # Wait exactly 1 second
    @wait(1000, 0, 200);      # Wait 1.0-1.2 seconds (randomized)
    ```

---

### `@time()`

Get current Unix timestamp.

**Parameters:** None

**Returns:** Float timestamp in seconds

!!! example
    ```macroni
    start = @time();
    # ... do work ...
    elapsed = @time() - start;
    @print("Took", elapsed, "seconds");
    ```

---

## Random Functions

### `@rand(min, max)`

Generate random float.

**Parameters:**

- `min` (float): Minimum value (inclusive)
- `max` (float): Maximum value (inclusive)

**Returns:** Random float in range

!!! example
    ```macroni
    delay = @rand(0.5, 2.0);
    @wait(@int(delay * 1000));
    ```

---

### `@rand_i(min, max)`

Generate random integer.

**Parameters:**

- `min` (int): Minimum value (inclusive)
- `max` (int): Maximum value (inclusive)

**Returns:** Random integer in range

!!! example
    ```macroni
    x = @rand_i(100, 500);
    y = @rand_i(100, 500);
    @mouse_move(x, y, 1000, true);
    ```

---

## Recording Functions

### `@record(name, start_btn, stop_btn)`

Record mouse and keyboard actions.

**Parameters:**

- `name` (string): Recording identifier
- `start_btn` (optional string): Key to start recording (default: `"space"`)
- `stop_btn` (optional string): Key to stop recording (default: `"esc"`)

**Returns:** None

**Cache:** Saved to `recordings_cache.json`

!!! example
    ```macroni
    @record("login_sequence");              # Space to start, Esc to stop
    @record("macro", "f1", "f2");           # F1 to start, F2 to stop
    ```

---

### `@playback(name, stop_btn)`

Replay recorded actions.

**Parameters:**

- `name` (string): Recording identifier
- `stop_btn` (optional string): Key to stop playback (default: `"esc"`)

**Returns:** None

!!! example
    ```macroni
    @playback("login_sequence");
    @playback("macro", "f3");               # F3 to stop
    ```

---

### `@recording_exists(name)`

Check if recording exists.

**Parameters:**

- `name` (string): Recording identifier

**Returns:** `true` if exists, `false` otherwise

!!! example
    ```macroni
    if !@recording_exists("macro") {
        @record("macro");
    }
    @playback("macro");
    ```

---

## List Functions

### `@len(collection)`

Get length of collection.

**Parameters:**

- `collection` (list, tuple, or string): Collection to measure

**Returns:** Integer length

!!! example
    ```macroni
    items = [1, 2, 3];
    @print(@len(items));        # 3
    @print(@len("hello"));      # 5
    ```

---

### `@append(list, item)`

Add item to end of list (modifies in place).

**Parameters:**

- `list` (list): List to modify
- `item` (any): Item to append

**Returns:** None

!!! example
    ```macroni
    items = [1, 2, 3];
    @append(items, 4);
    # items is now [1, 2, 3, 4]
    ```

---

### `@pop(list)` / `@pop(list, index)`

Remove and return item from list.

**Parameters:**

- `list` (list): List to modify
- `index` (optional int): Index to remove (default: -1, last item)

**Returns:** Removed item

!!! example
    ```macroni
    items = [1, 2, 3];
    last = @pop(items);         # last = 3, items = [1, 2]
    first = @pop(items, 0);     # first = 1, items = [2]
    ```

---

### `@shuffle(collection)`

Return shuffled copy of collection.

**Parameters:**

- `collection` (list or tuple): Collection to shuffle

**Returns:** New shuffled list

!!! example
    ```macroni
    original = [1, 2, 3, 4];
    shuffled = @shuffle(original);
    # original unchanged, shuffled is randomized
    ```

---

### `@swap(list, i, j)`

Swap two elements in a list.

**Parameters:**

- `list` (list): List to modify
- `i` (int): First index
- `j` (int): Second index

**Returns:** None

!!! example
    ```macroni
    items = [1, 2, 3];
    @swap(items, 0, 2);
    # items is now [3, 2, 1]
    ```

---

### `@copy(collection)`

Create shallow copy of collection.

**Parameters:**

- `collection` (list or tuple): Collection to copy

**Returns:** New collection with same elements

!!! example
    ```macroni
    original = [1, 2, 3];
    duplicate = @copy(original);
    @append(duplicate, 4);
    # original still [1, 2, 3], duplicate is [1, 2, 3, 4]
    ```

---

## Type Checking

### `@is_int(val)` / `@is_float(val)` / `@is_str(val)` / `@is_list(val)` / `@is_tuple(val)`

Check value type.

**Parameters:**

- `val` (any): Value to check

**Returns:** `true` if value matches type, `false` otherwise

!!! example
    ```macroni
    x = 42;
    if @is_int(x) {
        @print("x is an integer");
    }

    items = [1, 2, 3];
    @print(@is_list(items));    # true
    @print(@is_tuple(items));   # false
    ```

---

## Type Conversion

### `@int(val)` / `@float(val)` / `@str(val)`

Convert value to specified type.

**Parameters:**

- `val` (any): Value to convert

**Returns:** Converted value

!!! example
    ```macroni
    x = @int(3.7);          # 3
    y = @float(5);          # 5.0
    s = @str(123);          # "123"

    n = @int("42");         # 42
    ```

---

## Utility Functions

### `@print(arg1, arg2, ...)`

Print values to console.

**Parameters:**

- `...args` (any): Variable number of arguments to print

**Returns:** None

!!! example
    ```macroni
    @print("Hello, world!");
    @print("X:", x, "Y:", y);
    ```
