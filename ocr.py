import re
import cv2
import numpy as np
import easyocr
from template_match import screenshot_bgr
import dataclasses
import time

# Create once (slow to init). For speed, keep it global.
reader = easyocr.Reader(['en'], gpu=True)  # set gpu=True if you have CUDA

def preprocess_for_ocr(bgr, upscale=1.0):
    # Often helps on UI text. Convert to a grayscale binary image.
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    interpolation = cv2.INTER_CUBIC if upscale > 1.0 else cv2.INTER_AREA
    gray = cv2.resize(gray, None, fx=upscale, fy=upscale, interpolation=interpolation)
    # gray = cv2.GaussianBlur(gray, (3, 3), 0)
    # Otsu threshold
    # _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return gray

@dataclasses.dataclass
class OCRResult:
    bbox: np.ndarray  
    text: str
    conf: float


def ocr_find_text(region=None, min_conf=0.45, filter: str = None, upscale=1.0) -> list[OCRResult]:
    bgr = screenshot_bgr(region=region, downscale=1.0)
    # blows up 2x for better OCR accuracy
    img = preprocess_for_ocr(bgr, upscale=upscale)

    # easyocr expects RGB or grayscale; we already have grayscale/binary
    results = reader.readtext(img)  # [(bbox, text, conf), ...]

    filtered_results = [(bbox, text, conf) for (bbox, text, conf) in results if conf >= min_conf]

    output: list[OCRResult] = []
    for bbox, t, c in filtered_results:
        # Check if this text matches our search
        if filter and filter.lower() not in t.lower():
            continue

        # Scale bbox coordinates back down by 2x
        pts = np.array(bbox, np.float32) / upscale
        pts = pts.astype(np.int32)
        # converts from bgr -> rgb
        pts = pts.reshape((-1, 1, 2))
        output.append(OCRResult(bbox=pts, text=t, conf=c))
    return output


if __name__ == "__main__":
    perf = time.perf_counter()
    # Example: search full screen
    results = ocr_find_text(region=None, min_conf=0.8, filter="run and debug")
    print(f"OCR found {len(results)} results in {time.perf_counter() - perf:.3f} seconds")
    # # Get the original screenshot for drawing
    # bgr = screenshot_bgr(region=None, downscale=1.0)

    # Draw bounding boxes scaled back to original coordinates
    # (preprocessing upscales by 2x, so we need to divide by 2)
    # for res in results:
    #     # Green for matches, gray for non-matches
    #     color = (0, 255, 0)
    #     thickness = 3 


    #     cv2.polylines(bgr, [res.bbox], isClosed=True, color=color, thickness=thickness)

    #     print(f"  Text: '{res.text}'")

    # cv2.imshow("OCR Results - Green=Match, Gray=Other Text", bgr)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
