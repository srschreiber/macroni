from pynput import mouse, keyboard
import time, threading, queue, dataclasses
from typing import Optional
from macroni.util.mouse_utils import move_mouse_to, distance
import pyautogui
import random

event_queue: "queue.Queue[RecordedEvent]" = queue.Queue()
stop_event = threading.Event()


@dataclasses.dataclass
class RecordedEvent:
    timestamp: float
    kind: str  # "mouse_move" | "mouse_click" | "key_down" | "key_up"
    key: str  # "move" | "Button.left" | "Key.space" | "a" ...
    action: str  # "move" | "down" | "up"
    to_coordinates: Optional[tuple[int, int]] = None
    from_coordinates: Optional[tuple[int, int]] = None
    duration_ms: Optional[int] = None  # time until next event (or next move)


def now() -> float:
    return time.perf_counter()


def drain_queue(q: "queue.Queue[RecordedEvent]") -> list[RecordedEvent]:
    out: list[RecordedEvent] = []
    while True:
        try:
            out.append(q.get_nowait())
        except queue.Empty:
            break
    return out


def squash_moves(
    events: list[RecordedEvent], distance_threshold: int = 50
) -> list[RecordedEvent]:
    """Squash consecutive mouse moves based on pixel distance from start of sequence.
    Preserves last move positions before non-move events (clicks, key presses, etc.)."""
    out: list[RecordedEvent] = []

    i = 0
    n = len(events)
    while i < n:
        e = events[i]
        if e.kind == "mouse_move":
            first = e
            start_pos = first.to_coordinates
            last = e
            j = i + 1

            # Collect moves until distance threshold exceeded or non-move event
            while j < n and events[j].kind == "mouse_move":
                current_pos = events[j].to_coordinates
                if start_pos and current_pos:
                    dist = distance(
                        start_pos[0], start_pos[1], current_pos[0], current_pos[1]
                    )
                    if dist > distance_threshold:
                        # Distance exceeded - stop here and start new sequence
                        break

                last = events[j]
                j += 1

            # Create squashed event from first to last (preserving final position)
            squashed = dataclasses.replace(
                last,
                from_coordinates=(
                    first.from_coordinates
                    if first.from_coordinates
                    else first.to_coordinates
                ),
            )
            out.append(squashed)
            i = j
        else:
            out.append(e)
            i += 1
    return out


def attach_durations(events: list[RecordedEvent]) -> list[RecordedEvent]:
    """Set duration_ms = time until next event (ms). Last event duration_ms = 0."""
    if not events:
        return events
    for i in range(len(events) - 1):
        dt = (events[i + 1].timestamp - events[i].timestamp) * 1000.0
        events[i].duration_ms = max(0, int(dt))
    events[-1].duration_ms = 0
    return events


# record -> squashes all mouse moves within distance threshold.
def record(
    distance_threshold: int = 50, start_button=None, stop_button=None
) -> list[RecordedEvent]:
    # load corresponding key for start/stop
    start_key = (
        keyboard.Key.space
        if start_button is None
        else getattr(keyboard.Key, start_button, start_button)
    )
    stop_key = (
        keyboard.Key.esc
        if stop_button is None
        else getattr(keyboard.Key, stop_button, stop_button)
    )

    global event_queue
    event_queue = queue.Queue()
    stop_event.clear()
    start_event = threading.Event()
    recording_started = {"flag": False}

    # Track last mouse position for from_coordinates
    last_pos = {"x": None, "y": None}

    def on_move(x, y):
        if not recording_started["flag"]:
            return
        from_x, from_y = last_pos["x"], last_pos["y"]
        from_coords = (
            (int(from_x), int(from_y))
            if from_x is not None and from_y is not None
            else None
        )
        event_queue.put(
            RecordedEvent(
                now(),
                "mouse_move",
                "move",
                "move",
                to_coordinates=(int(x), int(y)),
                from_coordinates=from_coords,
            )
        )
        last_pos["x"], last_pos["y"] = x, y

    def on_click(x, y, button, pressed):
        if not recording_started["flag"]:
            return
        event_queue.put(
            RecordedEvent(
                now(),
                "mouse_click",
                str(button),
                "down" if pressed else "up",
                to_coordinates=(int(x), int(y)),
            )
        )

    def on_press(key):
        if not recording_started["flag"] and key == start_key:
            recording_started["flag"] = True
            start_event.set()
            print(f"\n✓ Recording started! Press {stop_button or 'ESC'} to stop.\n")
            return

        if recording_started["flag"] and key == stop_key:
            stop_event.set()
            return False

        if recording_started["flag"]:
            event_queue.put(RecordedEvent(now(), "key_down", str(key), "down"))

    def on_release(key):
        if recording_started["flag"]:
            event_queue.put(RecordedEvent(now(), "key_up", str(key), "up"))

    print(f"Press {start_button or 'SPACE'} to start recording...")

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    mouse_listener.start()
    keyboard_listener.start()

    # Wait for start button
    start_event.wait()

    # Initialize last_pos to current mouse position after starting
    x, y = pyautogui.position()
    last_pos["x"], last_pos["y"] = x, y
    event_queue.put(
        RecordedEvent(
            now(),
            "mouse_move",
            "move",
            "move",
            to_coordinates=(int(x), int(y)),
            from_coordinates=None,
        )
    )

    # Wait for stop button
    while not stop_event.is_set():
        time.sleep(0.01)

    # stop listeners (safe even if keyboard already stopped via return False)
    keyboard_listener.stop()
    mouse_listener.stop()

    events = drain_queue(event_queue)

    # ensure correct interleaving across threads
    events.sort(key=lambda e: e.timestamp)

    # squash move spam, then compute timing for replay
    events = squash_moves(events, distance_threshold=distance_threshold)
    events = attach_durations(events)

    print(f"✓ Recording stopped! Captured {len(events)} events (compressed).\n")
    return events


def parse_key_string(key_str: str):
    """Parse key string like 'Key.space' or \"'a'\" into pynput key object."""
    try:
        if key_str.startswith("Key."):
            # Special key like "Key.space", "Key.esc"
            key_name = key_str.replace("Key.", "")
            return getattr(keyboard.Key, key_name, None)
        elif key_str.startswith("'") and key_str.endswith("'"):
            # Character key like "'a'"
            return key_str[1:-1]  # Strip quotes
        else:
            # Fallback: return as-is
            return key_str
    except Exception:
        return None


def hallucinate_points(x1, y1, x2, y2, num_points):
    # randomly select n points between (x1, y1) and (x2, y2)
    points = []
    for _ in range(num_points):
        t = random.uniform(0, 1)
        x = x1 + t * (x2 - x1) + random.uniform(-3, 3)
        y = y1 + t * (y2 - y1) + random.uniform(-3, 3)
        points.append((x, y))
    points.sort(key=lambda p: ((p[0] - x1) ** 2 + (p[1] - y1) ** 2))
    return points


def playback(events: list[RecordedEvent], stop_button: str = "esc", jitter=1):
    print("Playing back...")
    mouse_controller = mouse.Controller()
    keyboard_controller = keyboard.Controller()

    if not events:
        print("No events to play back.")
        return

    # Setup stop button listener
    stop_key = (
        getattr(keyboard.Key, stop_button, keyboard.Key.esc)
        if stop_button
        else keyboard.Key.esc
    )
    stop_playback = threading.Event()

    def on_press(key):
        if key == stop_key:
            print(f"\n✓ Playback stopped by user.\n")
            stop_playback.set()
            return False

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()

    # first, move the mouse quickly to the start position
    first_move = next(
        (e for e in events if e.kind == "mouse_move" and e.to_coordinates), None
    )
    if first_move and first_move.to_coordinates:
        new_first = first_move.to_coordinates[0] + random.uniform(
            -jitter, jitter
        ), first_move.to_coordinates[1] + random.uniform(-5, 5)
        # overwrite first_move to include scatter
        first_move.to_coordinates = new_first
        move_mouse_to(new_first[0], new_first[1], pps=800, humanLike=True)

    print("Starting playback...")

    # Track timing relative to the first event
    first_event_timestamp = events[0].timestamp
    playback_start_time = now()

    for e in events:
        # Check if user requested stop
        if stop_playback.is_set():
            break

        # Calculate when this event should occur relative to playback start
        event_should_occur_at = e.timestamp - first_event_timestamp
        actual_elapsed = now() - playback_start_time

        # Wait if we're ahead of schedule
        wait_time = event_should_occur_at - actual_elapsed
        if wait_time > 0:
            time.sleep(wait_time)

        # Execute the event
        if e.kind == "mouse_move" and e.to_coordinates:
            # For mouse moves, use consistent speed since timing is handled by the wait above
            # splice in a few fake points to make movement slightly more random
            dist = distance(
                mouse_controller.position[0],
                mouse_controller.position[1],
                e.to_coordinates[0],
                e.to_coordinates[1],
            )
            # all_points = hallucinate_points(
            #     mouse_controller.position[0], mouse_controller.position[1],
            #     e.to_coordinates[0], e.to_coordinates[1],
            #     num_points = int(dist) // 10 # approximately one point every 10 pixels
            # )
            all_points = []
            all_points.append(e.to_coordinates)
            # Use consistent speed - timing is already handled by the wait logic above
            pps = 2000  # consistent pixels per second for smooth, human-like movement
            for pt in all_points:
                move_mouse_to(pt[0], pt[1], pps, True)
            # move_mouse_to(e.to_coordinates[0] + random.uniform(-jitter, jitter), e.to_coordinates[1] + random.uniform(-jitter, jitter), 3000, True)
        elif e.kind == "mouse_click" and e.to_coordinates:
            button = getattr(mouse.Button, e.key.split(".")[-1])
            if e.action == "down":
                mouse_controller.press(button)
            else:
                mouse_controller.release(button)
        elif e.kind == "key_down":
            key = parse_key_string(e.key)
            if key:
                keyboard_controller.press(key)
        elif e.kind == "key_up":
            key = parse_key_string(e.key)
            if key:
                keyboard_controller.release(key)

    keyboard_listener.stop()

    if not stop_playback.is_set():
        print("Playback finished.")
    else:
        print("Playback interrupted.")
