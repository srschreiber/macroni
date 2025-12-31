# Macroni

DSL for GUI automation with OCR, template matching, and screen interaction. Human-like randomness is baked into all operations, such as cubic bezier curved mouse movements and playback. It supports debugging line by line, expression evaluation (REPL), and abstracts complex implementation details such as computer vision and movement. It is a full on interpreted language described in EBNF, parsed using Lark, and executed by a tree-walking interpreter in Python.

It works on Linux, Mac, and Windows without any special setup required other than having Python. 

## Installation

### 1. Install Python Dependencies


```bash
pip install macroni
```

Note that pytorch for CPU is installed by default. If your NVIDIA GPU supports CUDA, you will have to manually reinstall pytorch for GPU.

To reinstall pytorch:
```bash
python -m pip uninstall -y torch torchvision torchaudio
```

Then reinstall with CUDA (may take some time)
```bash
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```


### 2. System Permissions

> **macOS:** System Preferences → Security & Privacy → Accessibility
>
> Grant permission to Terminal/Python to control your computer

### 3. VSCode Extension

For syntax highlighting, please add the extension to vscode: Macroni Language Support

## 4. Usage

### Basic Command

#### Interactive

The following command will allow REPL (Read-Eval-Print Loop)
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

## OCR Text Search 

Find and click text on screen:

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

Note: This operation is fairly slow without CUDA. If using a CPU, keeping the region as small as possible will improve performance greatly. 

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

## Template Matching

Easily find the position of images on the screen by uploading pictures to your template directory. 

Templates folder structure:
```
templates/
  └── login_button/
      ├── ex1.png
      └── ex2.png
```

Or more generally:
```
TEMPLATE_DIR/
  └── TEMPLATE_NAME/
      ├── template_sample1.png
      └── template_sample2.png
```

```macroni
@set_template_dir("./templates");
x, y = @find_template("login_button");

if x != null {
    @mouse_move(x, y, 1000, true);
    @left_click();
}
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
if x > 10 || x < 5 {
    @print("yes");
} else {
    @print("no");
}

if x > 10 && x < 20 {
    @print("x between 10 and 20);
}

while x < 100 {
    x = x + 1;
    if x > 50 {
        break;
    }
}

# Functions
fn click_button(x, y) {
    @mouse_move(x, y, 500, true);
    @left_click();
    return 13
}

# Outer scope copies variable from nearest scope
x = 5;
fn outer_x() {
    outer x;
    x = x + 5;
}
@print(x); # modified x
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
- `@record(name, start_btn, stop_btn, squash_distance)` - Record mouse/keyboard (squash_distance defaults to 50 pixels)
- `@playback(name, stop_btn)` - Replay recording

**Lists:**
- `@len(list)`, `@append(list, item)`, `@pop(list, index)`, `@shuffle(list)`

## Human-Like Randomness

Macroni incorporates randomness to avoid detection and mimic natural user behavior:

**Mouse Movement:**
```macroni
@mouse_move(x, y, 1000, true);  # human_like=true enables randomness
```
- Uses smoothstep for natural acceleration/deceleration
- Uses Bezier curves with random bulge combined with subtle sin movements

**Wait Times:**
```macroni
@wait(1000, (100, 300));  # Base delay + random 100-300ms
```
- Optional random range parameter adds variability to timing
- Prevents predictable patterns in automation

**Recording Playback:**
- Mouse movements are compressed squashed during recording and replayed using random paths while respecting timing and actions and precision
- Each new playback generates a different mouse path, never the exact same trajectory

## Cache Files

Auto-created in working directory:
- `regions_cache.json` - OCR regions
- `coordinates_cache.json` - Captured coordinates
- `pixel_colors_cache.json` - Captured colors
- `recordings_cache.json` - Recorded macros
