# Macroni

A domain-specific language for GUI automation, macro recording, and screen interaction.

> **Note:** Must grant permission for VS Code to control computer and receive input (System Preferences → Security & Privacy → Accessibility)

## Features

- **Template Matching** - Find UI elements on screen using image templates
- **Mouse & Keyboard Control** - Automate clicks, movements, and key presses
- **Interactive Setup** - Capture coordinates and colors with persistent caching
- **Record & Playback** - Record complex interactions and replay them
- **Human-Like Behavior** - Randomization and curved mouse movements
- **Simple Syntax** - Easy to learn, powerful automation capabilities

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Your First Script

Create `hello.macroni`:

```macroni
# Print a message
@print("Hello, Macroni!");

# Wait 1 second
@wait(1000);

# Move mouse and click
@mouse_move(500, 300, 1000, 1);
@wait(100);
@left_click();
```

### Run It

```bash
python macroni_interpret.py
```

## Basic Example: Click a Button

```macroni
# Set template directory
@set_template_dir("./templates");

# Find button on screen
x, y = @find_template("login_button");

if x != null {
    # Move mouse to button
    @mouse_move(x, y, 1000, 1);
    @wait(100);

    # Click it
    @left_click();
    @print("Button clicked!");
}
```

## Template Matching Setup

1. Create a templates folder:
```
templates/
  └── login_button/
      ├── ex1.png
      ├── ex2.png
      └── ex3.png
```

2. Capture screenshots of the UI element you want to find
3. Crop and save them in a folder (folder name = template identifier)
4. Use `@find_template("login_button")` in your script

## Language Features

### Data Types
- Numbers (int/float)
- Strings
- Tuples (immutable)
- Lists (mutable)
- null

### Control Flow
```macroni
# If statements
if x > 10 {
    @print("Greater");
}

# While loops
counter = 0;
while counter < 5 {
    @print(counter);
    counter = counter + 1;
}
```

### Functions
```macroni
fn greet(name) {
    @print("Hello,", name);
}

greet("Alice");
```

### Multiple Assignment
```macroni
# Tuples
x, y = (100, 200);

# From functions
coords_x, coords_y = @find_template("button");
r, g, b = @get_pixel_at(500, 300);
```

## Built-in Functions

### Output
- `@print(arg1, arg2, ...)` - Print to console

### Timing
- `@wait(ms)` - Wait with optional randomization
- `@time()` - Get current timestamp

### Random
- `@rand(min, max)` - Random float
- `@rand_i(min, max)` - Random integer

### Mouse
- `@mouse_move(x, y, speed, human_like)` - Move mouse
- `@left_click()` - Click mouse

### Keyboard
- `@send_input(type, key, action)` - Send input
- `@press_and_release(delay, ...keys)` - Press key combinations

### Template Matching
- `@set_template_dir(path)` - Set template directory
- `@find_template(name)` - Find single template
- `@find_templates(name, top_k)` - Find multiple templates

### Interactive Capture
- `@get_coordinates(label, use_cache)` - Capture coordinates
- `@get_pixel_color(alias, use_cache)` - Capture pixel color

### Pixel Operations
- `@get_pixel_at(x, y)` - Get RGB at coordinates
- `@check_pixel_color(x, y, radius, r, g, b, tolerance)` - Check for color

### Recording
- `@record(name, start_btn, stop_btn)` - Record macro
- `@playback(name, stop_btn)` - Play macro
- `@recording_exists(name)` - Check if recording exists

### Collections
- `@len(collection)` - Get length
- `@append(list, item)` - Add to list
- `@pop(list, index)` - Remove from list
- `@shuffle(collection)` - Shuffle collection

## Documentation

- [Full Language Documentation](docs/LANGUAGE.md)
- [Template Matching Guide](docs/TEMPLATE_MATCHING.md)
- [Built-in Functions Reference](docs/FUNCTIONS.md)
- [Examples](examples/)

## Examples

Check the `examples/` directory for complete scripts:

- `click_button.macroni` - Basic template matching and clicking
- `automated_login.macroni` - Multi-step automation
- `pixel_monitor.macroni` - Color detection loop
- `random_clicks.macroni` - Randomized behavior
- `record_replay.macroni` - Recording and playback
- `interactive_setup.macroni` - Using coordinate caching

## Cache Files

Macroni creates cache files in the working directory:

- `coordinates_cache.json` - Saved coordinates
- `pixel_colors_cache.json` - Saved colors
- `recordings_cache.json` - Saved macros

These persist between runs for faster execution.

## Best Practices

1. **Always check for null** when using template matching
2. **Add delays** between actions for reliability
3. **Use caching** to avoid re-prompting for coordinates
4. **Add randomization** for human-like behavior
5. **Organize templates** with descriptive folder names
6. **Create functions** for reusable logic

## Contributing

Contributions welcome! Feel free to open issues or submit pull requests.

## License

MIT
