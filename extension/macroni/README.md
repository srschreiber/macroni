# Macroni Language Support for VS Code

This extension provides language support for Macroni, an automation scripting language.

## Features

- **Syntax Highlighting**: Full syntax highlighting for Macroni keywords, functions, operators, and more
- **Auto-completion**: Snippets for all built-in functions and common patterns
- **Bracket Matching**: Automatic closing of brackets, parentheses, and quotes
- **Code Folding**: Support for folding code blocks
- **Comment Support**: Line comments with `#`

## Installation

### Option 1: Local Installation

1. Copy this extension folder to your VS Code extensions directory:
   - **macOS/Linux**: `~/.vscode/extensions/`
   - **Windows**: `%USERPROFILE%\.vscode\extensions\`

2. Restart VS Code

### Option 2: Development Mode

1. Open this folder in VS Code
2. Press `F5` to launch a new VS Code window with the extension loaded

## Supported File Extensions

- `.macroni`

## Language Features

### Keywords
- `fn`: Function definition
- `if`, `else`: Conditionals
- `while`: Loops
- `null`, `true`, `false`: Constants

### Built-in Functions

All built-in functions start with `@`:

#### Mouse & Input
- `@mouse_move(x, y, speed, humanLike)`: Move mouse to coordinates
- `@left_click()`: Perform left click
- `@send_input(type, key, action)`: Send keyboard/mouse input
- `@press_and_release(delay_ms, ...keys)`: Press and release keys

#### Screen & Template Matching
- `@find_template(name)`: Find single template on screen
- `@find_templates(name, top_k)`: Find multiple templates
- `@set_template_dir(path)`: Set template directory
- `@get_coordinates(message, use_cache)`: Get coordinates interactively
- `@capture_region(key, overwrite)`: Capture screen region
- `@ocr_find_text(region, min_conf, filter, upscale)`: Find text via OCR

#### Pixel Color
- `@check_pixel_color(x, y, radius, r, g, b, tolerance)`: Check pixel color in radius
- `@get_pixel_color(alias, use_cache)`: Get pixel color interactively
- `@get_pixel_at(x, y)`: Get pixel color at exact coordinates

#### Timing & Randomness
- `@wait(duration, min_random, max_random)`: Wait with optional randomization
- `@time()`: Get current timestamp
- `@rand(min, max)`: Generate random float
- `@rand_i(min, max)`: Generate random integer

#### Collections
- `@len(container)`: Get length of tuple/list/string
- `@shuffle(container)`: Shuffle tuple or list
- `@append(list, item)`: Append to list
- `@pop(list, index)`: Pop from list
- `@swap(list, idx1, idx2)`: Swap two elements
- `@copy(value)`: Create a copy

#### Recording & Playback
- `@record(name, start_btn, stop_btn)`: Record mouse/keyboard actions
- `@playback(name, stop_btn)`: Playback recorded actions
- `@recording_exists(name)`: Check if recording exists

#### Utilities
- `@print(...values)`: Print values
- `@foreach_tick(tick_provider, func)`: Execute function on each tick

### Snippets

Type the prefix and press Tab to expand:

- `fn` - Function definition
- `if` - If statement
- `ifelse` - If-else statement
- `while` - While loop
- `@print` - Print statement
- `@wait` - Wait statement
- `@mouse_move` - Mouse move
- `@find_template` - Find template
- And many more...

## Example Code

```macroni
# Define a function
fn click_target() {
    x, y = @find_template("button");
    if x != null {
        @mouse_move(x, y, 1200, true);
        @wait(100, 50);
        @left_click();
    }
}

# Main program
@print("Starting automation...");
@wait(2000);

running = true;
while running {
    click_target();
    @wait(1000);
}
```

## Grammar Reference

Based on the Macroni EBNF grammar:

- **Variables**: `name = value;`
- **Multiple assignment**: `x, y = value;` (destructuring)
- **Operators**: `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Data types**: Numbers, strings, lists `[]`, tuples `()`, `null`, `true`, `false`
- **Indexing**: `container[index]`
- **Comments**: `# comment text`

## Known Issues

None at this time.

## Contributing

Feel free to submit issues or pull requests to improve this extension.

## License

MIT
