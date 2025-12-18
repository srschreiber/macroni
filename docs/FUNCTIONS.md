# Built-in Functions Reference

## OCR Functions

### @capture_region(key, overwrite_cache)
Interactive region capture with caching.
- Hover top-left → Enter → bottom-right → Enter
- Returns `(x1, y1, x2, y2)`
- Cached in `regions_cache.json`

```macroni
region = @capture_region("search_box", false);  # Use cache
region = @capture_region("search_box", true);   # Force recapture
```

### @ocr_find_text(region, min_conf, filter, upscale)
Find text using OCR.
- `region`: `(x1,y1,x2,y2)` or `null` for full screen
- `min_conf`: 0.0-1.0 (0.8 recommended)
- `filter`: Substring or `null`
- `upscale`: 1.0 = default, 0.5 = faster, 2.0 = tiny text
- Returns `[(text, conf, [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]), ...]`

```macroni
results = @ocr_find_text(region, 0.8, "Login", 1.0);
if @len(results) > 0 {
    text, conf, bbox = results[0];
    x, y = bbox[0];
}
```

**GPU:** Edit `ocr.py` line 10: `reader = easyocr.Reader(['en'], gpu=True)`

---

## Mouse

### @mouse_move(x, y, speed, human_like)
- `speed`: pixels/second
- `human_like`: `1` for curved path, `0` for straight

### @left_click()
Click at current position.

---

## Keyboard

### @press_and_release(delay_ms, ...keys)
```macroni
@press_and_release(50, "ctrl", "c");  # Copy
```

### @send_input(type, key, action)
Low-level input.
- `type`: "keyboard" or "mouse"
- `action`: "press", "release", "click"

---

## Template Matching

### @set_template_dir(path)
```macroni
@set_template_dir("./templates");
```

### @find_template(name) or @find_template(name, left, top, width, height)
Returns `(x, y)` or `(null, null)`.

### @find_templates(name, top_k)
Returns tuple of `(x, y)` pairs.

---

## Screen

### @get_coordinates(label, use_cache)
Interactive coordinate capture.
- `use_cache`: `1` = use cache, `0` = recapture
- Cached in `coordinates_cache.json`

### @get_pixel_at(x, y)
Returns `(r, g, b)`.

### @get_pixel_color(alias, use_cache)
Interactive color capture.

### @check_pixel_color(x, y, radius, r, g, b, tolerance)
Returns `1` if found, `0` otherwise.

---

## Timing

### @wait(ms) or @wait(ms, random_min, random_max)
```macroni
@wait(1000);           # 1 second
@wait(1000, 0, 200);   # 1-1.2 seconds
```

### @time()
Returns timestamp (float).

---

## Random

### @rand(min, max)
Random float.

### @rand_i(min, max)
Random integer (inclusive).

---

## Recording

### @record(name, start_btn, stop_btn)
Record mouse/keyboard. Defaults: space to start, esc to stop.

### @playback(name, stop_btn)
Replay recording.

### @recording_exists(name)
Returns `1` if exists.

---

## Lists

### @len(collection)
Length of list, tuple, or string.

### @append(list, item)
Add to end (modifies in place).

### @pop(list) or @pop(list, index)
Remove and return item.

### @shuffle(collection)
Returns shuffled copy.

---

## Print

### @print(arg1, arg2, ...)
Print to console.
