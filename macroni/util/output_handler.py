from pynput import mouse, keyboard
import time, threading, queue, dataclasses
from typing import Optional
from macroni.util.mouse_utils import move_mouse_to, distance
import pyautogui

event_queue: "queue.Queue[RecordedEvent]" = queue.Queue()
stop_event = threading.Event()

@dataclasses.dataclass
class RecordedEvent:
    timestamp: float
    kind: str              # "mouse_move" | "mouse_click" | "key_down" | "key_up"
    key: str               # "move" | "Button.left" | "Key.space" | "a" ...
    action: str            # "move" | "down" | "up"
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

def squash_moves(events: list[RecordedEvent], bucket_size_ms: int = 50) -> list[RecordedEvent]:
    """Keep only the last mouse_move within each bucket window, preserving from_coordinates from first move."""
    out: list[RecordedEvent] = []
    bucket_s = bucket_size_ms / 1000.0

    i = 0
    n = len(events)
    while i < n:
        e = events[i]
        if e.kind == "mouse_move":
            bucket_end = e.timestamp + bucket_s
            first = e
            last = e
            j = i + 1
            while j < n and events[j].kind == "mouse_move" and events[j].timestamp <= bucket_end:
                last = events[j]
                j += 1
            # Create a new event with from_coordinates from first and to_coordinates from last
            squashed = dataclasses.replace(
                last,
                from_coordinates=first.from_coordinates if first.from_coordinates else first.to_coordinates
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

def record(bucket_size_ms: int = 50) -> list[RecordedEvent]:
    global event_queue
    event_queue = queue.Queue()
    stop_event.clear()

    # Track last mouse position for from_coordinates
    last_pos = {'x': None, 'y': None}

    def on_move(x, y):
        from_x, from_y = last_pos['x'], last_pos['y']
        from_coords = (int(from_x), int(from_y)) if from_x is not None and from_y is not None else None
        event_queue.put(RecordedEvent(
            now(),
            "mouse_move",
            "move",
            "move",
            to_coordinates=(int(x), int(y)),
            from_coordinates=from_coords
        ))
        last_pos['x'], last_pos['y'] = x, y

    def on_click(x, y, button, pressed):
        event_queue.put(RecordedEvent(
            now(),
            "mouse_click",
            str(button),
            "down" if pressed else "up",
            to_coordinates=(int(x), int(y)),
        ))

    def on_press(key):
        if key == keyboard.Key.esc:
            stop_event.set()
            return False
        event_queue.put(RecordedEvent(now(), "key_down", str(key), "down"))

    def on_release(key):
        event_queue.put(RecordedEvent(now(), "key_up", str(key), "up"))

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    print("Recording... press Esc to stop.")
    # Initialize last_pos to current mouse position
    x, y = pyautogui.position()
    last_pos['x'], last_pos['y'] = x, y
    event_queue.put(RecordedEvent(
        now(),
        "mouse_move",
        "move",
        "move",
        to_coordinates=(int(x), int(y)),
        from_coordinates=None
    ))
    mouse_listener.start()
    keyboard_listener.start()

    while not stop_event.is_set():
        time.sleep(0.01)

    # stop listeners (safe even if keyboard already stopped via return False)
    keyboard_listener.stop()
    mouse_listener.stop()

    events = drain_queue(event_queue)

    # ensure correct interleaving across threads
    events.sort(key=lambda e: e.timestamp)

    # squash move spam, then compute timing for replay
    events = squash_moves(events, bucket_size_ms=bucket_size_ms)
    events = attach_durations(events)

    print(f"Stopped. Final events: {len(events)}")
    return events

def playback(events: list[RecordedEvent]):
    print("Playing back...")
    mouse_controller = mouse.Controller()
    keyboard_controller = keyboard.Controller()

    if not events:
        print("No events to play back.")
        return

    # first, move the mouse quickly to the start position
    first_move = next((e for e in events if e.kind == "mouse_move" and e.to_coordinates), None)
    if first_move and first_move.to_coordinates:
        current_pos = pyautogui.position()
        dist = distance(
            current_pos[0], current_pos[1],
            first_move.to_coordinates[0], first_move.to_coordinates[1]
        )
        pps = 3000
        move_mouse_to(first_move.to_coordinates[0], first_move.to_coordinates[1], pps, True)

    print("Starting playback...")

    # Track timing relative to the first event
    first_event_timestamp = events[0].timestamp
    playback_start_time = now()

    for e in events:
        # Calculate when this event should occur relative to playback start
        event_should_occur_at = (e.timestamp - first_event_timestamp)
        actual_elapsed = now() - playback_start_time

        # Wait if we're ahead of schedule
        wait_time = event_should_occur_at - actual_elapsed
        if wait_time > 0:
            time.sleep(wait_time)

        # Execute the event
        if e.kind == "mouse_move" and e.to_coordinates:
            # For mouse moves, use fast movement since we've already waited
            move_mouse_to(e.to_coordinates[0], e.to_coordinates[1], 3000, True)
        elif e.kind == "mouse_click" and e.to_coordinates:
            button = getattr(mouse.Button, e.key.split(".")[-1])
            if e.action == "down":
                mouse_controller.press(button)
            else:
                mouse_controller.release(button)
        elif e.kind == "key_down":
            key = eval(e.key)
            keyboard_controller.press(key)
        elif e.kind == "key_up":
            key = eval(e.key)
            keyboard_controller.release(key)

    print("Playback finished.")

events = record(bucket_size_ms=50)
