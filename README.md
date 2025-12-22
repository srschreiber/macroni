# Macroni

DSL for GUI automation with OCR, template matching, and screen interaction.

## Installation

### 1. Install Python Dependencies


```bash
pip install macroni
```

Note that pytorch for CPU is installed by default. If your NVIDIA GPU supports CUDA, you will have to manually reinstall pytorch for GPU.


### 2. System Permissions

> **macOS:** System Preferences → Security & Privacy → Accessibility
>
> Grant permission to Terminal/Python to control your computer

### 3. VSCode Extension

For syntax highlighting, please add the extension to vscode: Macroni Language Support

## 4. Usage

### Basic Command

#### Interactive
```bash
macroni
```

#### Execute file

```bash
macroni --file script.macroni
```

Note: the first time running will take time because pytorch is a massive library. 

### Debug Mode

Enable interactive debugging with breakpoints:

```bash
# Enable debug mode
macroni --file script.macroni --debug

# Set breakpoints at specific lines
macroni --file script.macroni --debug --breakpoints 10 --breakpoints 25

# Or use short flags
macroni -f script.macroni -d -b 10 -b 25
```

**Debug Commands:**
- `n` (next) - Execute next line
- `c` (continue) - Continue to next breakpoint
- `p <var>` (print) - Print variable value
- `q` (quit) - Exit debugger
- `eval <expression>` - Evaluate expression

## OCR Text Search (Recommended)

Find and click text on screen without templates:

```macroni
# Capture region once, reuse forever (cached)
region = @capture_region("login_area", false);

# Find text in region
results = @ocr_find_text(region, 0.8, "Login", 1.0);

if @len(results) > 0 {
    text, conf, bbox = results[0];
    x1, y1 = bbox[0];
    @mouse_move(x1, y1, 500, true);
    @left_click();
}
```

**OCR Functions:**
- `@capture_region(key, overwrite)` - Interactive region capture with caching
  - Hover top-left → Enter → bottom-right → Enter
  - Returns `(x1, y1, x2, y2)` tuple
- `@ocr_find_text(region, min_conf, filter, upscale)` - Find text via OCR
  - `region`: From `@capture_region()` or `null` for full screen
  - `min_conf`: 0.0-1.0 confidence threshold
  - `filter`: Text substring to search for (case-insensitive)
  - `upscale`: 1.0 = no scaling, 0.5 = faster, 2.0 = tiny text
  - Returns `[(text, conf, [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]), ...]`

## Template Matching (Alternative)

```macroni
@set_template_dir("./templates");
x, y = @find_template("login_button");

if x != null {
    @mouse_move(x, y, 1000, true);
    @left_click();
}
```

Templates folder structure:
```
templates/
  └── login_button/
      ├── ex1.png
      └── ex2.png
```

## Language Basics

```macroni
# Variables & types
x = 10;
name = "test";
coords = (100, 200);
items = [1, 2, 3];

# Booleans
enabled = true;   # true = 1
disabled = false; # false = 0

# Destructuring
x, y = (100, 200);
text, conf, bbox = results[0];

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
fn click_button(x, y) {
    @mouse_move(x, y, 500, true);
    @left_click();
}
```

## Key Functions

**Mouse/Keyboard:**
- `@mouse_move(x, y, speed, human_like)`
- `@left_click()`
- `@press_and_release(delay_ms, ...keys)`

**Screen:**
- `@get_coordinates(label, use_cache)` - Interactive coordinate capture
- `@get_pixel_at(x, y)` - Returns `(r, g, b)`
- `@check_pixel_color(x, y, radius, r, g, b, tolerance)`

**Timing:**
- `@wait(ms)` or `@wait(ms, random_range)`
- `@time()`

**Recording:**
- `@record(name, start_btn, stop_btn)` - Record mouse/keyboard
- `@playback(name, stop_btn)` - Replay recording

**Lists:**
- `@len(list)`, `@append(list, item)`, `@pop(list, index)`, `@shuffle(list)`

## Cache Files

Auto-created in working directory:
- `regions_cache.json` - OCR regions
- `coordinates_cache.json` - Captured coordinates
- `pixel_colors_cache.json` - Captured colors
- `recordings_cache.json` - Recorded macros
