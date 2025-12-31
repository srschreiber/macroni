# Example: Pixel Color Monitor

This example demonstrates continuous monitoring of a screen location for a specific color, useful for detecting UI state changes.

## Features

- Pixel color checking with `@check_pixel_color()`
- Color tolerance for variations
- Continuous monitoring loop
- Status updates

## Code

```macroni
# Example: Pixel Color Monitoring
# Continuously monitors a pixel location for a specific color

@print("=== Pixel Color Monitor ===");

# Configuration
target_x = 500;
target_y = 300;
check_radius = 5;

# Target color (red in this example)
target_r = 255;
target_g = 0;
target_b = 0;
tolerance = 20;  # Allow some color variation

@print("Monitoring pixel at:", target_x, target_y);
@print("Looking for color RGB(", target_r, target_g, target_b, ")");
@print("Tolerance:", tolerance);
@print("Radius:", check_radius, "pixels");
@print("");
@print("Press Ctrl+C to stop");
@print("");

# Monitor loop
checks = 0;
while 1 {
    # Check if target color exists in radius
    found = @check_pixel_color(target_x, target_y, check_radius, target_r, target_g, target_b, tolerance);

    if found {
        @print("COLOR DETECTED at check #", checks);

        # Get exact color at center
        r, g, b = @get_pixel_at(target_x, target_y);
        @print("Exact color: RGB(", r, g, b, ")");

        # Take action when color is detected
        @print("Taking action...");
        @wait(1000);

        # Reset or continue monitoring
        @print("Continuing monitoring...");
    }

    # Check every 100ms
    @wait(100);
    checks = checks + 1;

    # Status update every 50 checks
    if checks % 50 == 0 {
        @print("Still monitoring... (", checks, "checks)");
    }
}
```

## How to Use

1. Find coordinates of the pixel to monitor
2. Set target RGB color values
3. Adjust `tolerance` for color matching flexibility
4. Run: `macroni pixel_monitor.macroni`
5. Press Ctrl+C to stop

## Use Cases

- Waiting for loading indicators to disappear
- Detecting health bar changes in games
- Monitoring notification indicators
- Detecting UI state transitions
