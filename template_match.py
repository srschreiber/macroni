import cv2
import numpy as np
import pyautogui
from mouse_utils import move_mouse_to
import time

def screenshot_scale(screen_bgr):
    img_h, img_w = screen_bgr.shape[:2]          # screenshot pixels
    scr_w, scr_h = pyautogui.size() # screen points
    return (img_w / scr_w), (img_h / scr_h)

def img_xy_to_screen_xy(x_img, y_img, sx, sy):
    return (x_img / sx, y_img / sy)

def screenshot_bgr(region=None, downscale=1.0):
    """
    region: (left, top, width, height) in screen coords, or None for full screen.
    returns: BGR uint8 image (OpenCV format)
    """
    im = pyautogui.screenshot(region=region)
    rgb = np.array(im)  # RGB
    # scale down 50% for performance
    if downscale != 1.0:
        new_w = int(rgb.shape[1] * downscale)
        new_h = int(rgb.shape[0] * downscale)
        rgb = cv2.resize(rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

def match_template_multiscale(
    screen_bgr: np.ndarray,
    template_bgr: np.ndarray,
    scales=np.linspace(0.7, 1.3, 25),
    method=cv2.TM_CCOEFF_NORMED,
    threshold=0.85,
    use_gray=True,
):
    """
    Returns dict with best match:
      {
        "found": bool,
        "score": float,
        "scale": float,
        "top_left": (x, y),
        "bottom_right": (x, y),
        "center": (x, y),
        "size": (w, h),
      }
    """
    if use_gray:
        screen = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
        template0 = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
    else:
        screen = screen_bgr
        template0 = template_bgr

    H, W = screen.shape[:2]
    th0, tw0 = template0.shape[:2]

    best = {
        "found": False,
        "score": -1.0,
        "scale": None,
        "top_left": None,
        "bottom_right": None,
        "center": None,
        "size": None,
    }

    for s in scales:
        tw = int(tw0 * s)
        th = int(th0 * s)
        if tw < 5 or th < 5:
            continue
        if tw > W or th > H:
            continue

        templ = cv2.resize(template0, (tw, th), interpolation=cv2.INTER_AREA)

        res = cv2.matchTemplate(screen, templ, method)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        score = max_val if method in (cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED) else -min_val
        loc = max_loc if method in (cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED) else min_loc

        if score > best["score"]:
            x, y = loc
            best.update({
                "score": float(score),
                "scale": float(s),
                "top_left": (int(x), int(y)),
                "bottom_right": (int(x + tw), int(y + th)),
                "center": (int(x + tw // 2), int(y + th // 2)),
                "size": (int(tw), int(th)),
            })

    best["found"] = best["score"] >= threshold
    return best

def get_template_examples(template_dir, template_name):
    """
    Returns list of file paths for template examples in the given directory.
    Directory name should be the template_name, all files in that target directory correspond to examples
    """
    import os
    target_dir = os.path.join(template_dir, template_name)
    if not os.path.isdir(target_dir):
        return []
    files = []
    for fname in os.listdir(target_dir):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            files.append(os.path.join(target_dir, fname))
    return files

def locate_one_template_on_screen(
    template_dir: str = "./templates",
    template_name: str = "default",
    scales=np.linspace(0.8, 1.2, 5),
    threshold=0.70,
    use_gray=False,
    downscale=.9,
) -> tuple | None:
    screen = screenshot_bgr(region=None, downscale=downscale)
    sx, sy = screenshot_scale(screen)

    # preload images
    imgs = [cv2.imread(p) for p in get_template_examples(template_dir, template_name)]
    # downscale templates for performance
    imgs = [cv2.resize(img, (0,0), fx=downscale, fy=downscale, interpolation=cv2.INTER_AREA) for img in imgs]
    print("Start locating")

    perf_counter = time.perf_counter()
    found = None
    for template in imgs:
        match = match_template_multiscale(
            screen, template,
            scales=scales,
            threshold=threshold,
            use_gray=use_gray,
        )

        if match["found"]:
            cx, cy = match["center"]
            mx, my = img_xy_to_screen_xy(cx, cy, sx, sy)
            found = (mx, my)
            break
    print(f"Locating took {time.perf_counter() - perf_counter:.3f} seconds")
    return found


if __name__ == "__main__":
    # Load template from disk
    template_dir = "/Users/sam.schreiber/src/macroni/templates"
    template_name = "test"

    pos = locate_one_template_on_screen(template_dir, template_name)
    if pos is not None:
        print(f"Template '{template_name}' found at screen position: {pos}")
        move_mouse_to(pos[0], pos[1], pps=5000, humanLike=True)
    else:
        print(f"Template '{template_name}' not found on screen.")


