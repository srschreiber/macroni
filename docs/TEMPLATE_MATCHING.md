# Template Matching Guide

> **Note:** For text-based UI elements, use OCR (`@capture_region` + `@ocr_find_text`) instead. Template matching is best for icons, images, and non-text elements.

## Setup

```
templates/
  └── button/
      ├── ex1.png
      └── ex2.png
```

1. Screenshot the UI element
2. Crop to show only the distinctive part
3. Save as `ex1.png`, `ex2.png`, etc. (multiple variations improve accuracy)
4. Use folder name as template identifier

## Usage

```macroni
@set_template_dir("./templates");

# Find single match
x, y = @find_template("button");

if x != null {
    @mouse_move(x, y, 1000, true);
    @left_click();
}

# Find multiple matches
matches = @find_templates("icon", 5);
count = @len(matches);

i = 0;
while i < count {
    x, y = matches[i];
    @mouse_move(x, y, 1000, true);
    @left_click();
    i = i + 1;
}

# Search specific region (faster)
x, y = @find_template("button", 0, 0, 960, 540);
```

## Tips

1. **Keep templates small** (50-200px typical)
2. **PNG format** (not JPEG - compression artifacts reduce accuracy)
3. **Capture at target resolution** (must match runtime display)
4. **Include variations** (hover state, different backgrounds, etc.)
5. **Make templates distinctive** (unique colors, shapes, icons)
6. **Use regions** to limit search area (improves speed and accuracy)
7. **Always check for null** before using coordinates

## Troubleshooting

- **Not found:** Element not visible, wrong resolution, or template not distinctive enough
- **False matches:** Template too generic - make more specific or use regions
- **Slow:** Template too large or searching full screen - use regions
- **Resolution issues:** Capture templates on target display
