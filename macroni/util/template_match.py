import cv2
import numpy as np
import pyautogui
import mss
from macroni.util.mouse_utils import move_mouse_to
import time
import os
from macroni.util.vision import Vision
import sys
import concurrent.futures


def screenshot_scale(screen_bgr, region=None):
    img_h, img_w = screen_bgr.shape[:2]  # screenshot pixels
    scr_w, scr_h = pyautogui.size()  # screen points
    return (img_w / scr_w), (img_h / scr_h)


def img_xy_to_screen_xy(x_img, y_img, sx, sy):
    return (x_img / sx, y_img / sy)


def screenshot_bgr(region=None, downscale=1.0, debug=False):
    """
    region: (left, top, width, height) in screen coords, or None for full screen.
    returns: BGR uint8 image (OpenCV format)
    Note: On retina displays, MSS captures at actual pixel resolution (2x logical resolution).
    The screenshot_scale function handles this by calculating the ratio between screenshot pixels
    and screen points, which is then used by img_xy_to_screen_xy to convert back correctly.
    """
    with mss.mss() as sct:
        if region is None:
            # Capture primary monitor
            monitor = sct.monitors[0]
        else:
            # region is (left, top, width, height) in screen points
            # MSS needs actual pixel coordinates, so scale by the display scaling factor
            # For retina displays, this is typically 2.0
            monitor = region

        # MSS returns BGRA on all platforms (Windows, macOS, Linux)
        # Drop alpha channel to get BGR format for OpenCV
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        bgr = img[:, :, :3]  # Keep first 3 channels (BGR), drop alpha

        # Apply downscaling for performance (if not already done above)
        if downscale != 1.0:
            new_w = int(bgr.shape[1] * downscale)
            new_h = int(bgr.shape[0] * downscale)
            bgr = cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            # Ensure contiguous array when no resize (OpenCV requires this)
            bgr = bgr.copy()

        return bgr


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
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            files.append(os.path.join(target_dir, fname))
    return files


template_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)


# just return center points of found templates
def locate_template_on_screen(
    template_dir: str = "./templates",
    template_name: str = "default",
    scales=np.linspace(0.8, 1.2, 5),
    threshold=0.8,
    use_gray=True,
    downscale=0.8,
    top_k=1,
    debug=False,
) -> tuple | None:
    total_perf_counter = time.perf_counter()
    perf_counter = time.perf_counter()
    screen = screenshot_bgr(region=None, downscale=downscale, debug=debug)
    sx, sy = screenshot_scale(screen, region=None)
    print(f"Screenshot took {time.perf_counter() - perf_counter:.3f} seconds")

    # Get template paths
    template_paths = get_template_examples(template_dir, template_name)
    print("Start locating")

    perf_counter = time.perf_counter()
    found = None

    # On macOS, templates are typically at 2x retina resolution, but MSS captures at 1x
    # So we need to scale templates by 0.5x to match MSS screenshots
    template_scale = downscale
    if sys.platform == "darwin":
        template_scale *= 0.5  # Compensate for retina resolution difference

    def find_in_template(template_path) -> list[Vision.VisionHit]:
        # Create Vision instance for this template
        # Scale template to match the screenshot resolution
        template_img = cv2.imread(template_path)
        if template_scale != 1.0:
            template_img = cv2.resize(
                template_img,
                (0, 0),
                fx=template_scale,
                fy=template_scale,
                interpolation=cv2.INTER_AREA,
            )
            # Save temporarily to create Vision instance
            temp_path = template_path.replace(".png", "_temp.png")
            cv2.imwrite(temp_path, template_img)
            vision = Vision(temp_path)
            os.remove(temp_path)
        else:
            vision = Vision(template_path)

        # Find matches using multiscale
        points = vision.find_multiscale(
            screen,
            scales=scales,
            threshold=threshold,
            use_gray=use_gray,
            find_one=False,
            debug_mode=debug,
        )
        return points

    # Collect all VisionHit results from parallel searches
    all_hits: list[Vision.VisionHit] = []
    futures = [
        template_thread_pool.submit(find_in_template, template_path)
        for template_path in template_paths
    ]
    for future in concurrent.futures.as_completed(futures):
        hits = future.result()
        all_hits.extend(hits)

    # Dedupe results using groupRectangles
    if len(all_hits) == 0:
        print(f"Locating took {time.perf_counter() - perf_counter:.3f} seconds")
        print(f"Total time: {time.perf_counter() - total_perf_counter:.3f} seconds")
        return []

    if len(all_hits) > 1:
        # Convert VisionHit bboxes to rectangles for grouping
        rectangles = []
        for hit in all_hits:
            x, y, w, h = hit.bbox
            rect = [int(x), int(y), int(w), int(h)]
            rectangles.append(rect)
            rectangles.append(
                rect
            )  # Add twice for groupRectangles to keep single boxes

        # Group overlapping rectangles
        grouped_rects, weights = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=0.5
        )

        # Extract deduplicated center points
        deduped_hits = []
        for x, y, w, h in grouped_rects:
            center_x = x + w // 2
            center_y = y + h // 2
            deduped_hits.append(
                Vision.VisionHit(bbox=(x, y, w, h), center=(center_x, center_y))
            )

        print(f"Templates found: {len(all_hits)} -> {len(deduped_hits)} after dedup")
    else:
        deduped_hits = all_hits

    # Convert to screen coordinates and return top_k center points only
    ret = []
    for hit in deduped_hits[:top_k]:
        x_img, y_img = hit.center
        x_screen, y_screen = img_xy_to_screen_xy(x_img, y_img, sx, sy)
        ret.append((int(x_screen), int(y_screen)))

    print(f"Locating took {time.perf_counter() - perf_counter:.3f} seconds")
    print(f"Total time: {time.perf_counter() - total_perf_counter:.3f} seconds")
    return ret


if __name__ == "__main__":
    # Load template from disk
    template_dir = "/Users/sam.schreiber/src/macroni/templates"
    template_name = "test"

    pos = locate_template_on_screen(template_dir, template_name, debug=True)
    if pos is not None:
        pos = pos[0]
        print(f"Template '{template_name}' found at screen position: {pos}")
        move_mouse_to(pos[0], pos[1], pps=5000, humanLike=True)
    else:
        print(f"Template '{template_name}' not found on screen.")
