# Macroni Examples

This directory contains example scripts demonstrating various Macroni features.

## Examples

### 1. click_button.macroni
**Basic template matching and clicking**

- Sets template directory
- Finds a button using template matching
- Moves mouse and clicks
- Error handling for template not found

**Prerequisites:** Create `templates/login_button/ex1.png` with a screenshot of your target button

**Run:** `python macroni_interpret.py examples/click_button.macroni`

---

### 2. automated_login.macroni
**Multi-step automation workflow**

- Defines reusable function for find-and-click
- Sequences multiple UI interactions
- Username field → Password field → Login button
- Error handling at each step

**Prerequisites:** Create templates for `username_field`, `password_field`, and `login_button`

---

### 3. pixel_monitor.macroni
**Color detection and monitoring loop**

- Continuously monitors a pixel location
- Checks for specific RGB color
- Uses tolerance for color matching
- Status updates during monitoring
- Demonstrates `@check_pixel_color` and `@get_pixel_at`

**Configuration:** Edit target coordinates and color in the script

---

### 4. random_clicks.macroni
**Human-like randomized behavior**

- Random click positions within bounds
- Random mouse speeds
- Random delays between actions
- Demonstrates `@rand_i` and natural automation patterns

**Use case:** Gaming automation, stress testing UIs

---

### 5. record_replay.macroni
**Recording and playback**

- Records mouse and keyboard actions
- Saves to cache file
- Replays recorded session
- Conditional logic based on recording existence

**Instructions:**
1. First run: Press SPACE to start recording, ESC to stop
2. Second run: Automatically replays recording

---

### 6. interactive_setup.macroni
**Interactive coordinate and color capture with caching**

- Uses `@get_coordinates` with caching
- Uses `@get_pixel_color` with caching
- First run: prompts user to set up coordinates/colors
- Subsequent runs: uses cached values
- Demonstrates cache-based workflows

**Benefits:** Set up once, run many times without re-prompting

---

## Running Examples

### Method 1: Modify macroni_interpret.py

Edit the `macroni_script()` function to return the contents of an example file:

```python
def macroni_script():
    with open('examples/click_button.macroni', 'r') as f:
        return f.read()
```

Then run:
```bash
python macroni_interpret.py
```

### Method 2: Create a CLI wrapper

Create `run_script.py`:

```python
import sys
from macroni_interpret import Interpreter, calc_parser

if len(sys.argv) < 2:
    print("Usage: python run_script.py <script.macroni>")
    sys.exit(1)

with open(sys.argv[1], 'r') as f:
    script = f.read()

interp = Interpreter()
tree = calc_parser.parse(script)
interp.eval(tree)
```

Then run:
```bash
python run_script.py examples/click_button.macroni
```

---

## Creating Your Own Examples

1. Copy an existing example as a starting point
2. Modify for your use case
3. Create necessary templates in `templates/` directory
4. Test thoroughly before production use

---

## Template Setup for Examples

For examples that use template matching, create this structure:

```
templates/
  ├── login_button/
  │   ├── ex1.png
  │   └── ex2.png
  ├── username_field/
  │   └── ex1.png
  └── password_field/
      └── ex1.png
```

See [Template Matching Guide](../docs/TEMPLATE_MATCHING.md) for detailed instructions on creating templates.

---

## Troubleshooting

### "Template not found"
- Verify `templates/` directory exists
- Check folder name matches template name in script
- Ensure at least one `ex*.png` file exists
- Make sure target UI element is visible on screen

### "Recording not found"
- Run the script once to create the recording
- Check that `recordings_cache.json` was created
- Verify recording name matches in script

### Interactive prompts not working
- Make sure terminal has focus
- Press Enter when prompted (not Return on some keyboards)
- Check that mouse is positioned correctly before pressing Enter

---

## Best Practices Demonstrated

1. **Always check for null** when using `@find_template`
2. **Use delays** between actions (`@wait`)
3. **Add randomization** for human-like behavior
4. **Create functions** for reusable logic
5. **Use caching** to avoid re-prompting users
6. **Error handling** at each step
7. **Descriptive messages** via `@print`

---

## Next Steps

After trying these examples:

1. Read the [Full Language Documentation](../docs/LANGUAGE.md)
2. Study the [Template Matching Guide](../docs/TEMPLATE_MATCHING.md)
3. Check the [Functions Reference](../docs/FUNCTIONS.md)
4. Build your own automation scripts!

---

## Contributing Examples

Have a cool example? Submit a pull request!

Requirements:
- Well-commented code
- Clear use case description
- Any necessary setup instructions
- No sensitive information or credentials
