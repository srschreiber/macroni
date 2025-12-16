from pynput import mouse, keyboard
import time, threading, queue, dataclasses
from typing import Optional

event_queue: "queue.Queue[RecordedEvent]" = queue.Queue()
stop_event = threading.Event()

@dataclasses.dataclass
class RecordedEvent:
    timestamp: float
    kind: str              # "mouse_move" | "mouse_click" | "key_down" | "key_up"
    key: str               # "move" | "Button.left" | "Key.space" | "a" ...
    action: str            # "move" | "down" | "up"
    coordinates: Optional[tuple[int, int]] = None
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
    """Keep only the last mouse_move within each bucket window."""
    out: list[RecordedEvent] = []
    bucket_s = bucket_size_ms / 1000.0

    i = 0
    n = len(events)
    while i < n:
        e = events[i]
        if e.kind == "mouse_move":
            bucket_end = e.timestamp + bucket_s
            last = e
            j = i + 1
            while j < n and events[j].kind == "mouse_move" and events[j].timestamp <= bucket_end:
                last = events[j]
                j += 1
            out.append(last)
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

    def on_move(x, y):
        event_queue.put(RecordedEvent(now(), "mouse_move", "move", "move", (int(x), int(y))))

    def on_click(x, y, button, pressed):
        event_queue.put(RecordedEvent(
            now(),
            "mouse_click",
            str(button),
            "down" if pressed else "up",
            (int(x), int(y)),
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

    for e in events:
        time.sleep(e.duration_ms / 1000.0 if e.duration_ms else 0)
        if e.kind == "mouse_move" and e.coordinates:
            mouse_controller.position = e.coordinates
        elif e.kind == "mouse_click" and e.coordinates:
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
