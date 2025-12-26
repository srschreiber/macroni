import re
import cv2
import numpy as np
import easyocr
from macroni.util.template_match import screenshot_bgr
import dataclasses
import time
import json
import os
from pynput import mouse


# Create once (slow to init). For speed, keep it global.
reader = easyocr.Reader(["en"], gpu=True)  # set gpu=True if you have CUDA

# Cache file for regions
REGIONS_CACHE_FILE = "regions_cache.json"


def preprocess_for_ocr(bgr, upscale=1.5, invert=None, close=False):
    # 1) upscale (helps small fonts)
    if upscale and upscale != 1.0:
        interp = cv2.INTER_CUBIC if upscale > 1.0 else cv2.INTER_AREA
        bgr = cv2.resize(bgr, None, fx=upscale, fy=upscale, interpolation=interp)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # 2) denoise (good on noisy backgrounds)
    gray = cv2.fastNlMeansDenoising(
        gray, None, h=12, templateWindowSize=7, searchWindowSize=21
    )

    # # 3) local contrast boost (CLAHE)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # gray = clahe.apply(gray)

    # # 4) remove slow-varying background (key step for noisy backgrounds)
    # # Choose kernel size relative to image size; bigger = more aggressive background removal.
    # h, w = gray.shape[:2]
    # k = max(15, (min(h, w) // 30) | 1)  # odd
    # bg = cv2.GaussianBlur(gray, (k, k), 0)
    # norm = cv2.addWeighted(gray, 1.5, bg, -0.5, 0)  # "unsharp" but background-aware

    # # 5) adaptive threshold handles non-uniform backgrounds better than Otsu
    # th = cv2.adaptiveThreshold(
    #     norm, 255,
    #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     cv2.THRESH_BINARY,
    #     31,  # blockSize (odd); try 21/31/41
    #     7    # C; try 3..10
    # )

    # # 6) optional invert if text is light-on-dark
    # if invert is True:
    #     th = 255 - th
    # elif invert is None:
    #     # auto-guess: if mostly white, assume black text on white background
    #     # if mostly black, assume white text on black background -> invert
    #     if np.mean(th) < 127:
    #         th = 255 - th

    # # 7) optional gentle morphology (use only if letters break up)
    # if close:
    #     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    #     th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)

    # save a picture for debugging
    # cv2.imwrite("ocr_debug.png", gray)
    return gray


def region_capture(
    region_key: str, overwrite_cache: bool = False
) -> tuple[int, int, int, int]:
    """
    Interactively capture a screen region with caching.
    Always writes to cache, but overwrite_cache controls whether to recapture.

    Args:
        region_key: Unique identifier for this region (used as cache key)
        overwrite_cache: If True, ignore cached value and recapture.
                        If False, use cached value if available.

    Returns:
        Tuple of (top_left_x, top_left_y, bottom_right_x, bottom_right_y)

    Usage:
        # First time or when overwrite_cache=True:
        # User hovers mouse over top-left corner and presses Enter
        # Then hovers over bottom-right corner and presses Enter

        region = region_capture("login_button")  # Uses cache if available
        region = region_capture("login_button", overwrite_cache=True)  # Forces recapture
        results = ocr_find_text(region=region, filter="Login")
    """
    # Load cache
    cache = {}
    if os.path.exists(REGIONS_CACHE_FILE):
        with open(REGIONS_CACHE_FILE, "r") as f:
            cache = json.load(f)

    # Return cached region if available and not overwriting
    if not overwrite_cache and region_key in cache:
        region = cache[region_key]
        print(f"Using cached region '{region_key}': {region}")
        return tuple(region)

    # Capture new region interactively
    print(f"\nCapturing region '{region_key}':")
    print("1. Hover mouse over TOP-LEFT corner and press ENTER...")
    input()

    # Get current mouse position for top-left
    listener = mouse.Controller()
    x1, y1 = listener.position
    print(f"   Top-left: ({x1}, {y1})")

    print("2. Hover mouse over BOTTOM-RIGHT corner and press ENTER...")
    input()

    # Get current mouse position for bottom-right
    x2, y2 = listener.position
    print(f"   Bottom-right: ({x2}, {y2})")

    # Ensure coordinates are in correct order
    top_left_x = min(x1, x2)
    top_left_y = min(y1, y2)
    bottom_right_x = max(x1, x2)
    bottom_right_y = max(y1, y2)

    region = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)

    # Always save to cache
    cache[region_key] = list(region)
    with open(REGIONS_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"Region '{region_key}' captured and cached: {region}\n")
    return region


@dataclasses.dataclass
class OCRResult:
    bbox: list[list[float]]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] - 4 corners
    text: str
    conf: float


def ocr_find_text(
    region: tuple[int, int, int, int] | None = None,
    min_conf: float = 0.45,
    filter: str | list | tuple | None = None,
    upscale: float = 1.0,
) -> list[OCRResult]:
    """
    Perform OCR on screen region with optional filtering.

    Args:
        region: Optional region tuple (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
               Can be obtained from region_capture() for faster, focused OCR.
               If None, captures full screen.
        min_conf: Minimum confidence threshold (0.0 to 1.0)
        filter: Optional text filter - only return results containing this substring
        upscale: Upscale factor for preprocessing (1.0 = no scaling, 2.0 = 2x larger)
                Lower values (e.g., 0.5) are faster but may miss small text.
                Higher values (e.g., 2.0) are slower but better for tiny text.

    Returns:
        List of OCRResult objects containing bounding boxes, text, and confidence scores

    Usage:
        # Full screen OCR
        results = ocr_find_text(filter="Login")

        # Region-specific OCR (much faster!)
        region = region_capture("search_box")
        results = ocr_find_text(region=region, filter="Search", upscale=1.0)
    """
    # Convert region tuple to dictionary format for screenshot_bgr
    region_dict = None
    if region is not None:
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = region
        region_dict = {
            "left": top_left_x,
            "top": top_left_y,
            "width": bottom_right_x - top_left_x,
            "height": bottom_right_y - top_left_y,
        }

    # try at + 20% and -20% upscales for robustness
    upscales = [upscale, upscale * 1.2, upscale * 0.8]
    for upscale in upscales:
        bgr = screenshot_bgr(region=region_dict, downscale=1.0)
        img = preprocess_for_ocr(bgr, upscale=upscale)

        # easyocr expects RGB or grayscale; we already have grayscale/binary
        results = reader.readtext(img)  # [(bbox, text, conf), ...]

        filtered_results = [
            (bbox, text, conf) for (bbox, text, conf) in results if conf >= min_conf
        ]

        if not filtered_results or len(filtered_results) == 0:
            continue

        # found confident results, return these
        output: list[OCRResult] = []
        for bbox, t, c in filtered_results:
            # Check if this text matches our search
            if filter:
                if isinstance(filter, (list, tuple)):
                    if not any(f.lower() in t.lower() for f in filter):
                        continue
                else:
                    if filter.lower() not in t.lower():
                        continue

            # Scale bbox coordinates back down by upscale factor
            pts = np.array(bbox, np.float32) / upscale

            # If region was specified, adjust coordinates to be relative to screen (not region)
            if region is not None:
                top_left_x, top_left_y, _, _ = region
                pts[:, 0] += top_left_x  # Add X offset
                pts[:, 1] += top_left_y  # Add Y offset

            # Convert to regular Python list for macroni compatibility (no numpy)
            bbox_list = [[float(x), float(y)] for x, y in pts]

            output.append(OCRResult(bbox=bbox_list, text=t, conf=float(c)))
        return output


if __name__ == "__main__":
    # Example 1: Interactive region capture with caching
    # This captures a region once and reuses it on subsequent runs (much faster!)
    print("=== Example: Region-based OCR with caching ===")
    region = region_capture("test_region", overwrite_cache=False)

    # Now perform OCR only on that region (much faster than full screen!)
    perf = time.perf_counter()
    results = ocr_find_text(region=region, min_conf=0.8, filter="run", upscale=1.0)
    elapsed = time.perf_counter() - perf

    print(f"\nOCR found {len(results)} results in {elapsed:.3f} seconds")
    for res in results:
        print(f"  - '{res.text}' (confidence: {res.conf:.2f})")

    # Example 2: Full screen OCR (slower but searches everywhere)
    # Uncomment to test:
    # print("\n=== Example: Full screen OCR ===")
    # perf = time.perf_counter()
    # results = ocr_find_text(region=None, min_conf=0.8, filter="run", upscale=1.0)
    # print(f"OCR found {len(results)} results in {time.perf_counter() - perf:.3f} seconds")
