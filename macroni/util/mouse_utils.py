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


def smooth_move_to_bezier_deterministic(x2, y2, total_time=0.25, hz=240):
    desired_time = total_time * 0.90
    x1, y1 = pyautogui.position()

    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    px, py = -uy, ux

    steps_time = max(1, int(desired_time * hz))
    steps_dist = int(max(8, min(steps_time, L * 0.35)))
    steps = max(1, min(steps_time, steps_dist))
    dt = desired_time / steps

    # deterministic control point (straight line)
    apex_t = 0.5
    arc_px = 0.0
    cx = x1 + dx * apex_t + px * arc_px
    cy = y1 + dy * apex_t + py * arc_px

    start = time.perf_counter()
    for i in range(1, steps + 1):
        t = i / steps
        omt = 1 - t
        bx = (omt * omt) * x1 + 2 * omt * t * cx + (t * t) * x2
        by = (omt * omt) * y1 + 2 * omt * t * cy + (t * t) * y2
        pyautogui.moveTo(int(bx), int(by), duration=0, _pause=False)

        target = start + i * dt
        now = time.perf_counter()
        if target > now:
            time.sleep(target - now)

    pyautogui.moveTo(x2, y2, duration=0, _pause=False)


# TODO: PLAYBACK MAKE END POINT MORE RANDOM
def smooth_move_to_bezier(
    x2,
    y2,
    total_time=0.25,
    hz=240,
    accuracy_pixels=1,
    arc_px=None,  # if None, chosen from distance
    arc_px_cap=80,
    wobble_px=2,  # max wobble amplitude in pixels
):
    desired_time = total_time * 0.8
    x1, y1 = pyautogui.position()

    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0

    if L * 0.1 < arc_px_cap:
        arc_px_cap = L * 0.1

    # Unit direction + perpendicular
    ux, uy = dx / L, dy / L
    px, py = -uy, ux

    # Steps (don’t oversample small moves)
    steps_time = max(1, int(desired_time * hz))
    steps_dist = int(max(8, min(steps_time, L * 0.35)))
    steps = max(1, min(steps_time, steps_dist))
    dt = desired_time / steps

    # --- Choose Bezier control points (cubic) ---
    # Pick two random points along the straight line, then push it sideways.
    apex_t1 = random.uniform(0.025, 0.975)  # where the arc "peaks" along the path
    arc_dir1 = random.choice([-1, 1])

    apex_t2 = random.uniform(0.025, 0.975)  # where the arc "peaks" along the path
    arc_dir2 = random.choice([-1, 1])

    if arc_px is None:
        # Sublinear arc scaling: grows with distance, but not crazy on long moves
        arc_px = (math.sqrt(L) * 5.0) * random.uniform(0.25, 1.0)
    arc_px1 = arc_dir1 * min(arc_px_cap, arc_px)
    arc_px2 = arc_dir2 * min(arc_px_cap, arc_px)

    cx1 = x1 + dx * apex_t1 + px * arc_px1
    cy1 = y1 + dy * apex_t1 + py * arc_px1
    cx2 = x1 + dx * apex_t2 + px * arc_px2
    cy2 = y1 + dy * apex_t2 + py * arc_px2

    # --- Wobble setup (tiny and damped) ---
    # allow max of one wobble per 100 pixels
    wobble_cycles_min = 0.5
    wobble_cycles_max = L / 100.0
    cycles = random.uniform(wobble_cycles_min, wobble_cycles_max)
    if L < 40:
        cycles = 0.0  # no wobble for tiny moves

    phase = random.uniform(0, 2 * math.pi)
    omega = 2 * math.pi * cycles / max(desired_time, 1e-3)

    start = time.perf_counter()
    for i in range(1, steps + 1):
        t = i / steps

        # stop early if close enough
        cxp, cyp = pyautogui.position()
        if math.hypot(x2 - cxp, y2 - cyp) <= accuracy_pixels:
            break

        # Quadratic Bezier point
        # B(t) = (1-t)^2 P0 + 2(1-t)t C + t^2 P1

        # Cubic Bezier point
        # B(t) = (1-t)^3 P0 + 3(1-t)^2 t C1 + 3(1-t) t^2 C2 + t^3 P1
        omt = 1 - t
        bx = (
            (omt * omt * omt) * x1
            + 3 * (omt * omt) * t * cx1
            + 3 * omt * (t * t) * cx2
            + (t * t * t) * x2
        )
        by = (
            (omt * omt * omt) * y1
            + 3 * (omt * omt) * t * cy1
            + 3 * omt * (t * t) * cy2
            + (t * t * t) * y2
        )

        # Perpendicular wobble (damped at ends, stronger mid-path)
        env = (4 * t * (1 - t)) ** 1.4  # near-zero at start/end
        # also fade out near the end more, so we "settle"
        settle = (1 - t) ** 1.6

        wob = 0.0
        if cycles > 0:
            wob = (
                wobble_px * env * settle * math.sin(phase + omega * (t * desired_time))
            )

        bx += px * wob
        by += py * wob

        pyautogui.moveTo(int(bx), int(by), duration=0, _pause=False)

        # timing
        target = start + i * dt
        now = time.perf_counter()
        if target > now:
            time.sleep(target - now)

    # Final correction (gentle settle)
    cxp, cyp = pyautogui.position()
    rem = math.hypot(x2 - cxp, y2 - cyp)
    elapsed = time.perf_counter() - start
    time_remaining = max(total_time - elapsed, 0.0)

    if rem > 2:
        pyautogui.moveTo(
            x2, y2, duration=min(0.06, max(0.01, time_remaining)), _pause=False
        )
    else:
        pyautogui.moveTo(x2, y2, duration=0, _pause=False)


def move_mouse_offset(x_offset: int, y_offset: int, pps: int, humanLike: bool) -> None:
    """Move the mouse cursor by the specified offsets at a rate of pps pixels per second."""
    current_x, current_y = pyautogui.position()
    duration = calc_duration(
        current_x, current_y, current_x + x_offset, current_y + y_offset, pps
    )
    new_x = current_x + x_offset
    new_y = current_y + y_offset
    move_mouse_to(new_x, new_y, pps, humanLike)


def move_mouse_to(
    x: int, y: int, pps: int, humanLike: bool, within_pixels: int = 1
) -> None:
    """Move the mouse cursor to the specified coordinates at a rate of pps pixels per second."""
    current_x, current_y = pyautogui.position()
    duration = calc_duration(current_x, current_y, x, y, pps)

    r = within_pixels * math.sqrt(random.random())
    theta = random.uniform(0, 2 * math.pi)

    dx = int(r * math.cos(theta))
    dy = int(r * math.sin(theta))

    x += dx
    y += dy
    if not humanLike:
        pyautogui.moveTo(x, y, duration=duration)
    else:
        smooth_move_to_bezier(x, y, total_time=duration)
