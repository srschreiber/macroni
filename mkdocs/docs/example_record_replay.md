# Example: Record and Replay

This example demonstrates recording user actions and playing them back automatically.

## Features

- Record mouse and keyboard actions with `@record()`
- Replay recorded macros with `@playback()`
- Check for existing recordings with `@recording_exists()`
- Persistent recording storage

## Code

```macroni
# Example: Recording and Replaying Macros
# Shows how to record user actions and play them back

@print("=== Record & Replay Example ===");

# Name for this recording
recording_name = "demo_macro";

# Check if recording already exists
if @recording_exists(recording_name) {
    @print("Recording '", recording_name, "' found in cache");
    @print("");
    @print("Playing back recording...");
    @print("(Press ESC to stop playback)");
    @playback(recording_name, "esc");
    @print("Playback complete!");
} else {
    @print("No recording found for '", recording_name, "'");
    @print("");
    @print("Let's create one!");
    @print("");
    @print("=== RECORDING MODE ===");
    @print("Instructions:");
    @print("1. Press SPACE to start recording");
    @print("2. Perform your actions (mouse moves, clicks, keys)");
    @print("3. Press ESC to stop recording");
    @print("");

    # Record with space to start, esc to stop
    @record(recording_name, "space", "esc");

    @print("");
    @print("Recording saved as '", recording_name, "'");
    @print("");
    @print("You can replay it by running this script again!");
}

@print("");
@print("=== Script Complete ===");
```

## How to Use

1. **First run** (Recording):
   - Run: `macroni record_replay.macroni`
   - Press SPACE to start recording
   - Perform your actions
   - Press ESC to stop

2. **Subsequent runs** (Playback):
   - Run the script again
   - Recording plays back automatically
   - Press ESC to stop playback

## Use Cases

- Repeating complex multi-step workflows
- Testing UI interactions
- Creating reusable macro sequences
- Automating repetitive manual tasks
