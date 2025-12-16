import cv2
import numpy as np
import pyautogui
from mouse_utils import move_mouse_to
import time
import os
from vision import Vision

def screenshot_scale(screen_bgr, region=None):
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
    im = pyautogui.screenshot(region=None)
    rgb = np.array(im)  # RGB
    # scale down 50% for performance
    if downscale != 1.0:
        new_w = int(rgb.shape[1] * downscale)
        new_h = int(rgb.shape[0] * downscale)
        rgb = cv2.resize(rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

def get_template_examples(template_dir, template_name):
    """
    Returns list of file paths for template examples in the given directory.
    Directory name should be the template_name, all files in that target directory correspond to examples
    """
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
    threshold=0.8,
    use_gray=False,
    downscale=.7,
) -> tuple | None:
    screen = screenshot_bgr(region=None, downscale=downscale)
    sx, sy = screenshot_scale(screen, region=None)

    # Get template paths
    template_paths = get_template_examples(template_dir, template_name)
    print("Start locating")

    perf_counter = time.perf_counter()
    found = None

    for template_path in template_paths:
        # Create Vision instance for this template
        # Need to downscale the template to match the downscaled screen
        template_img = cv2.imread(template_path)
        if downscale != 1.0:
            template_img = cv2.resize(template_img, (0,0), fx=downscale, fy=downscale, interpolation=cv2.INTER_AREA)
            # Save temporarily to create Vision instance
            temp_path = template_path.replace('.png', '_temp.png')
            cv2.imwrite(temp_path, template_img)
            vision = Vision(temp_path)
            os.remove(temp_path)
        else:
            vision = Vision(template_path)

        # Find matches using multiscale
        points = vision.find_multiscale(screen, scales=scales, threshold=threshold, use_gray=use_gray)

        if points:
            # Take first match
            cx, cy = points[0]
            print(f"Template found image coords: ({cx}, {cy})")

            # Convert to screen coordinates
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


