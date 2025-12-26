import cv2 as cv
import numpy as np
import dataclasses


class Vision:

    # properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    # constructor
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED):
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        # Drop alpha channel if present (ensure 3-channel BGR for consistency)
        if len(self.needle_img.shape) == 3 and self.needle_img.shape[2] == 4:
            self.needle_img = self.needle_img[:, :, :3].copy()

        # Save the dimensions of the needle image
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, haystack_img, threshold=0.5, debug_mode=None):
        # run the OpenCV algorithm
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        # print(locations)

        # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
        # locations by using groupRectangles().
        # First we need to create the list of [x, y, w, h] rectangles
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)
        # Apply group rectangles.
        # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
        # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
        # in the result. I've set eps to 0.5, which is:
        # "Relative difference between sides of the rectangles to merge them into a group."
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        # print(rectangles)

        points = []
        if len(rectangles):
            # print('Found needle.')

            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            marker_color = (255, 0, 255)
            marker_type = cv.MARKER_CROSS

            # Loop over all the rectangles
            for x, y, w, h in rectangles:

                # Determine the center position
                center_x = x + int(w / 2)
                center_y = y + int(h / 2)
                # Save the points
                points.append((center_x, center_y))

                if debug_mode == "rectangles":
                    # Determine the box position
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    # Draw the box
                    cv.rectangle(
                        haystack_img,
                        top_left,
                        bottom_right,
                        color=line_color,
                        lineType=line_type,
                        thickness=2,
                    )
                elif debug_mode == "points":
                    # Draw the center point
                    cv.drawMarker(
                        haystack_img,
                        (center_x, center_y),
                        color=marker_color,
                        markerType=marker_type,
                        markerSize=40,
                        thickness=2,
                    )

        if debug_mode:
            cv.imshow("Matches", haystack_img)
            # cv.waitKey()
            # cv.imwrite('result_click_point.jpg', haystack_img)

        return points

    @dataclasses.dataclass
    class VisionHit:
        bbox: tuple[int, int, int, int]  # (x, y, w, h)
        center: tuple[int, int]  # (center_x, center_y)

    def find_multiscale(
        self,
        haystack_img,
        scales=None,
        threshold=0.5,
        use_gray=True,
        find_one=False,
        debug_mode=None,
    ) -> list[VisionHit]:
        """
        Find needle in haystack at multiple scales.
        Returns list of (x, y) center points for matches found.
        """
        if scales is None:
            scales = np.linspace(0.7, 1.3, 10)

        # Convert to grayscale if requested
        if use_gray:
            if len(haystack_img.shape) == 3:
                haystack = cv.cvtColor(haystack_img, cv.COLOR_BGR2GRAY)
            else:
                haystack = haystack_img
            if len(self.needle_img.shape) == 3:
                needle = cv.cvtColor(self.needle_img, cv.COLOR_BGR2GRAY)
            else:
                needle = self.needle_img
        else:
            haystack = haystack_img
            needle = self.needle_img

        H, W = haystack.shape[:2]
        needle_h, needle_w = needle.shape[:2]

        # Efficient path for find_one: just get the best match
        if find_one:
            for scale in scales:
                scaled_w = int(needle_w * scale)
                scaled_h = int(needle_h * scale)

                # Skip invalid sizes
                if scaled_w < 5 or scaled_h < 5:
                    continue
                if scaled_w > W or scaled_h > H:
                    continue

                # Resize needle to current scale
                scaled_needle = cv.resize(
                    needle, (scaled_w, scaled_h), interpolation=cv.INTER_AREA
                )

                # Match template
                result = cv.matchTemplate(haystack, scaled_needle, self.method)

                # Get best match using minMaxLoc
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

                # For TM_SQDIFF and TM_SQDIFF_NORMED, best match is min, otherwise max
                if self.method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
                    best_val = min_val
                    best_loc = min_loc
                else:
                    best_val = max_val
                    best_loc = max_loc

                # Check if best match exceeds threshold
                if best_val >= threshold:
                    x, y = best_loc
                    center_x = x + scaled_w // 2
                    center_y = y + scaled_h // 2

                    if debug_mode:
                        marker_color = (255, 0, 255)
                        marker_type = cv.MARKER_CROSS
                        cv.drawMarker(
                            haystack_img,
                            (center_x, center_y),
                            color=marker_color,
                            markerType=marker_type,
                            markerSize=40,
                            thickness=2,
                        )
                        cv.imshow("Multiscale Matches", haystack_img)

                    return [
                        Vision.VisionHit(
                            bbox=(x, y, scaled_w, scaled_h),
                            center=(center_x, center_y),
                        )
                    ]

            return []

        # Original path for finding all matches
        all_rectangles = []

        # Try each scale
        for scale in scales:
            scaled_w = int(needle_w * scale)
            scaled_h = int(needle_h * scale)

            # Skip invalid sizes
            if scaled_w < 5 or scaled_h < 5:
                continue
            if scaled_w > W or scaled_h > H:
                continue

            # Resize needle to current scale
            scaled_needle = cv.resize(
                needle, (scaled_w, scaled_h), interpolation=cv.INTER_AREA
            )

            # Match template
            result = cv.matchTemplate(haystack, scaled_needle, self.method)

            # Find locations above threshold
            locations = np.where(result >= threshold)
            locations = list(zip(*locations[::-1]))

            # Convert to rectangles with actual scaled dimensions
            for loc in locations:
                rect = [int(loc[0]), int(loc[1]), scaled_w, scaled_h]
                all_rectangles.append(rect)
                all_rectangles.append(rect)  # Add twice for groupRectangles

            if len(all_rectangles) > 0:
                break

        # Group overlapping rectangles
        if len(all_rectangles) == 0:
            return []

        rectangles, weights = cv.groupRectangles(
            all_rectangles, groupThreshold=1, eps=0.5
        )

        points: list[Vision.VisionHit] = []
        if len(rectangles):
            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            marker_color = (255, 0, 255)
            marker_type = cv.MARKER_CROSS

            for x, y, w, h in rectangles:
                center_x = x + int(w / 2)
                center_y = y + int(h / 2)
                # points.append((center_x, center_y))
                points.append(
                    Vision.VisionHit(
                        bbox=(x, y, w, h),
                        center=(center_x, center_y),
                    )
                )

                if debug_mode == "rectangles":
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    cv.rectangle(
                        haystack_img,
                        top_left,
                        bottom_right,
                        color=line_color,
                        lineType=line_type,
                        thickness=2,
                    )
                elif debug_mode == "points":
                    cv.drawMarker(
                        haystack_img,
                        (center_x, center_y),
                        color=marker_color,
                        markerType=marker_type,
                        markerSize=40,
                        thickness=2,
                    )

        if debug_mode:
            cv.imshow("Multiscale Matches", haystack_img)

        return points
