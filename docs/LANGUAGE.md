# Macroni Language Reference

## Syntax Basics

```macroni
# Comments start with #
x = 10;                    # Statements end with semicolon
name = "test";             # Strings in double quotes
enabled = true;            # Booleans: true (1), false (0)
coords = (100, 200);       # Tuples (immutable)
items = [1, 2, 3];         # Lists (mutable)
nothing = null;            # Null value

# Destructuring
x, y = (100, 200);
text, conf, bbox = results[0];

# Operators
a = 10 + 5 - 2 * 3 / 2;    # Arithmetic
b = x > 10;                # Comparison: returns 1 or 0
c = items[0];              # Indexing

# Control flow
if x > 10 {
    @print("yes");
} else {
    @print("no");
}

while x < 100 {
    x = x + 1;
}

# Functions
fn click_at(x, y) {
    @mouse_move(x, y, 500, true);
    @left_click();
}
```

## OCR Text Detection

**Recommended approach** for finding UI elements:

```macroni
# 1. Capture region once (cached forever)
region = @capture_region("login_area", false);

# 2. Find text with OCR
results = @ocr_find_text(region, 0.8, "Login", 1.0);

# 3. Click first match
if @len(results) > 0 {
    text, conf, bbox = results[0];
    x, y = bbox[0];  # Top-left corner
    @mouse_move(x, y, 500, true);
    @left_click();
}
```

### @capture_region(key, overwrite_cache)

Interactively capture screen region with caching.

**Interactive flow:**
1. Hover mouse over top-left corner
2. Press Enter
3. Hover mouse over bottom-right corner
4. Press Enter

**Parameters:**
- `key`: Unique identifier (cached in `regions_cache.json`)
- `overwrite_cache`: `true` to recapture, `false` to use cache

**Returns:** `(top_left_x, top_left_y, bottom_right_x, bottom_right_y)`

### @ocr_find_text(region, min_conf, filter, upscale)

Find text on screen using OCR.

**Parameters:**
- `region`: From `@capture_region()` or `null` for full screen
- `min_conf`: 0.0-1.0 confidence threshold (0.8 recommended)
- `filter`: Substring to search for (case-insensitive), or `null` for all text
- `upscale`: Scaling factor
  - `1.0` = no scaling (default, fastest)
  - `0.5` = downscale for speed
  - `2.0` = upscale for tiny text

**Returns:** `[(text, conf, [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]), ...]`
- Coordinates are screen-relative (ready for mouse movement)
- Bounding box has 4 corners

**GPU Acceleration:**
Edit `ocr.py` line 10 to enable GPU (much faster):
```python
reader = easyocr.Reader(['en'], gpu=True)  # Requires CUDA
```

## Template Matching (Alternative)

Use when OCR isn't suitable (icons, non-text elements):

```macroni
@set_template_dir("./templates");
x, y = @find_template("button");

if x != null {
    @mouse_move(x, y, 1000, true);
    @left_click();
}
```

Templates: `templates/button/ex1.png`, `templates/button/ex2.png`, etc.

## Core Functions

**Mouse/Keyboard:**
- `@mouse_move(x, y, speed, human_like)` - Move cursor
- `@left_click()` - Click
- `@press_and_release(delay_ms, ...keys)` - Keyboard shortcuts

**Screen:**
- `@get_coordinates(label, use_cache)` - Interactive coordinate capture
- `@get_pixel_at(x, y)` - RGB at position
- `@check_pixel_color(x, y, radius, r, g, b, tolerance)` - Color match

**Timing:**
- `@wait(ms)` or `@wait(ms, random_min, random_max)` - Delay
- `@time()` - Current timestamp

**Lists:**
- `@len(list)`, `@append(list, item)`, `@pop(list, index)`, `@shuffle(list)`

**Recording:**
- `@record(name, start_btn, stop_btn)` - Record actions
- `@playback(name, stop_btn)` - Replay actions

## Cache Files

Auto-created in working directory:
- `regions_cache.json` - OCR regions from `@capture_region()`
- `coordinates_cache.json` - Points from `@get_coordinates()`
- `pixel_colors_cache.json` - Colors from `@get_pixel_color()`
- `recordings_cache.json` - Macros from `@record()`

Delete to reset, or use `overwrite_cache`/`use_cache` parameters.
