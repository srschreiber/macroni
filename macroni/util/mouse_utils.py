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

def smooth_move_to(x2, y2, total_time=0.25, hz=200, jitter_px=9, arc_strength=0.1, accuracy_pixels=1):
    desired_time = total_time * 0.90
    x1, y1 = pyautogui.position()

    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)

    ux, uy = dx / (L or 1.0), dy / (L or 1.0)
    px, py = -uy, ux

    # distance-aware steps (cap both ways)
    steps_time = max(1, int(desired_time * hz))
    steps_dist = int(max(8, min(steps_time, L * 0.6)))  # ~0.6 steps per px, capped
    steps = max(1, min(steps_time, steps_dist))

    dt = desired_time / steps

    # target scatter
    x2j = x2 + random.randint(-accuracy_pixels, accuracy_pixels)
    y2j = y2 + random.randint(-accuracy_pixels, accuracy_pixels)

    dx, dy = x2j - x1, y2j - y1
    L = math.hypot(dx, dy) or 1.0

    # arc setup
    arc_dir = random.choice([-1, 1])
    strength_rand = random.uniform(0.7, 1.3)
    peak = arc_dir * arc_strength*strength_rand * L
    peak = max(-100, min(100, peak))

    peak_pos = random.uniform(0.25, 0.75)

    # wobble setup
    cycles = random.uniform(.5, 1.0)
    if L < 20:
        cycles = random.uniform(0.25, .5)

    wobble_dir = random.choice([-1, 1])
    phase = random.uniform(0, 2 * math.pi)
    omega0 = 2 * math.pi * cycles / max(desired_time, 0.001)

    start = time.perf_counter()
    for i in range(1, steps + 1):
        t = i / steps

        # if distance remaining is very small like < 5 pixels, move directly to target
        cx, cy = pyautogui.position()
        rem = math.hypot(x2j - cx, y2j - cy)
        if rem <= accuracy_pixels:
            break

        # smoothstep base motion
        tt = t * t * (3 - 2 * t)
        x = x1 + dx * tt
        y = y1 + dy * tt

        # smooth bump for the bulge (C1-ish, no cusp): bell-shaped around peak_pos
        # width controls how wide the bulge is; randomize slightly
        width = random.uniform(0.25, 0.45)
        z = (t - peak_pos) / max(width, 1e-6)
        bulge_factor = math.exp(-z * z * 3.0)  # gaussian-ish bump
        bulge = peak * bulge_factor

        # Wobble envelope and amplitude
        env = 4 * t * (1 - t)
        base_amp = min(jitter_px, 0.03 * L)
        wobble_amp = base_amp * (1 - t) ** 1.2

        # Bounded omega noise (no random-walk drift)
        omega = omega0 * (1.0 + random.uniform(-0.08, 0.08))
        phase += omega * dt

        wobble = wobble_dir * wobble_amp * env * math.sin(phase)

        x += px * (bulge + wobble)
        y += py * (bulge + wobble)

        pyautogui.moveTo(int(x), int(y), duration=0, _pause=False)

        target = start + i * dt
        now = time.perf_counter()
        if target > now:
            time.sleep(target - now)

    # Final correction only if still noticeably off
    cx, cy = pyautogui.position()
    rem = math.hypot(x2 - cx, y2 - cy)
    elapsed = time.perf_counter() - start
    time_remaining = max(total_time - elapsed, 0.0)

    if rem > 2:
        pyautogui.moveTo(x2, y2, duration=min(0.06, max(0.01, time_remaining)), _pause=False)
    else:
        pyautogui.moveTo(x2, y2, duration=0, _pause=False)


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
    