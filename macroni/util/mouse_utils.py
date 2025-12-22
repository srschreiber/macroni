import pyautogui
import random
import time

def distance(x1: int, y1: int, x2: int, y2: int) -> float:
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def calc_duration(x1: int, y1: int, x2: int, y2: int, pps: int) -> float:
    _distance = distance(x1, y1, x2, y2)
    if _distance == 0:
        return 0.0
    return _distance / pps if pps > 0 else 0.0

import random
import math

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def smooth_move_to(x2, y2, total_time=0.25, hz=150, jitter_px=7, arc_strength=0.04, accuracy_pixels=1):
    desired_time = total_time*.90 # encourage moving faster because easier to sleep than to catch up
    x1, y1 = pyautogui.position()
    x1 += random.randint(-accuracy_pixels, accuracy_pixels)
    y1 += random.randint(-accuracy_pixels, accuracy_pixels)
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0

    ux, uy = dx / L, dy / L
    px, py = -uy, ux

    steps = max(1, int(desired_time * hz))
    dt = desired_time / steps

    arc_dir = random.choice([-1, 1])
    peak = arc_dir * arc_strength * L
    peak = max(-60, min(60, peak))

    cycles = random.uniform(1.0, 4.0)
    wobble_dir = random.choice([-1, 1])

    phase = random.uniform(0, 2 * math.pi)
    omega = 2 * math.pi * cycles / max(desired_time, 0.001)  # rad/s

    start = time.perf_counter()
    for i in range(1, steps + 1):

        t = i / steps

        # smoothstep along the line
        tt = t*t*(3 - 2*t)
        x = x1 + dx * tt
        y = y1 + dy * tt

        # big arc (0 at ends)
        bulge = peak * (4 * t * (1 - t))

        # mini-arc wobble (also 0 at ends)
        env = 4 * t * (1 - t)

        # scale wobble to distance and fade near end
        base_amp = min(jitter_px, 0.03 * L)
        wobble_amp = base_amp * (1 - t)**1.2

        # phase drift (relative)
        omega += random.uniform(-0.15, 0.15) * omega * dt
        phase += omega * dt

        wobble = wobble_dir * wobble_amp * env * math.sin(phase)

        x += px * (bulge + wobble)
        y += py * (bulge + wobble)

        pyautogui.moveTo(round(x), round(y), duration=0, _pause=False)
        target = start + i * dt
        now = time.perf_counter()
        if target > now:
            time.sleep(target - now)
        
        # # if we're running late or within 2% of desired time, break
        # if time.perf_counter() - start >= desired_time:
        #     break

    print("done move")
    elapsed = time.perf_counter() - start
    time_remaining = max(total_time - elapsed, 0.05)

    # final_dur = max(0.01, min(0.05, time_remaining))
    pyautogui.moveTo(x2, y2, duration=time_remaining, _pause=False)


def move_mouse_offset(x_offset: int, y_offset: int, pps: int, humanLike: bool) -> None:
    """Move the mouse cursor by the specified offsets at a rate of pps pixels per second."""
    current_x, current_y = pyautogui.position()
    duration = calc_duration(current_x, current_y, current_x + x_offset, current_y + y_offset, pps)
    new_x = current_x + x_offset
    new_y = current_y + y_offset
    move_mouse_to(new_x, new_y, pps, humanLike)

def move_mouse_to(x: int, y: int, pps: int, humanLike: bool) -> None:
    """Move the mouse cursor to the specified coordinates at a rate of pps pixels per second."""
    current_x, current_y = pyautogui.position()
    duration = calc_duration(current_x, current_y, x, y, pps)
    if not humanLike:
        pyautogui.moveTo(x, y, duration=duration)
    else:
        smooth_move_to(x, y, total_time=duration)
    