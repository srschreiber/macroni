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

### 2. pixel_monitor.macroni
**Color detection and monitoring loop**

- Continuously monitors a pixel location
- Checks for specific RGB color
- Uses tolerance for color matching
- Status updates during monitoring
- Demonstrates `@check_pixel_color` and `@get_pixel_at`

**Configuration:** Edit target coordinates and color in the script

---

### 3. random_clicks.macroni
**Human-like randomized behavior**

- Random click positions within bounds
- Random mouse speeds
- Random delays between actions
- Demonstrates `@rand_i` and natural automation patterns

**Use case:** Gaming automation, stress testing UIs

---

### 4. record_replay.macroni
**Recording and playback**

- Records mouse and keyboard actions
- Saves to cache file
- Replays recorded session
- Conditional logic based on recording existence

**Instructions:**
1. First run: Press SPACE to start recording, ESC to stop
2. Second run: Automatically replays recording

---

### 5. interactive_setup.macroni
**Interactive coordinate and color capture with caching**

- Uses `@get_coordinates` with caching
- Uses `@get_pixel_color` with caching
- First run: prompts user to set up coordinates/colors
- Subsequent runs: uses cached values
- Demonstrates cache-based workflows

**Benefits:** Set up once, run many times without re-prompting