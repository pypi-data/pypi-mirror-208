#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      visual_test
   Description:
   Author:          dingyong.cui
   date：           2023/5/6
-------------------------------------------------
   Change Activity:
                    2023/5/6
-------------------------------------------------
"""
import logging
import math
import os
import time
import uuid
from concurrent import futures
from pathlib import Path
from typing import Union, List

import cv2
import fitz
import imutils
import numpy as np
import pytesseract
from skimage import metrics

from visual_compare.doc.image.compare_image import CompareImage
from visual_compare.utils.common import is_url

logger = logging.getLogger(__name__)


class VisualTest(object):
    ROBOT_LIBRARY_VERSION = 0.2
    BORDER_FOR_MOVE_TOLERANCE_CHECK = 0
    DPI_DEFAULT = 200
    WATERMARK_WIDTH = 25
    WATERMARK_HEIGHT = 30
    WATERMARK_CENTER_OFFSET = 3 / 100
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    BOTTOM_LEFT_CORNER_OF_TEXT = (20, 60)
    FONT_SCALE = 0.7
    FONT_COLOR = (255, 0, 0)
    LINE_TYPE = 2
    THRESHOLD = 0.95
    REFERENCE_LABEL = "Expected Result (Reference)"
    CANDIDATE_LABEL = "Actual Result (Candidate)"
    OCR_ENGINE = "tesseract"
    MOVEMENT_DETECTION = "classic"

    def __init__(self, threshold: float = 0.0000, dpi: int = DPI_DEFAULT, take_screenshots: bool = False,
                 show_diff: bool = False, ocr_engine: str = OCR_ENGINE, movement_detection: str = MOVEMENT_DETECTION,
                 watermark_file: str = None, screenshot_dir: str = None, screenshot_format: str = 'jpg', **kwargs):
        """
        | =Arguments= | =Description= |
        | ``take_screenshots`` | Shall screenshots be taken also for passed comparisons.   |
        | ``show_diff`` | Shall a diff screenshot be added showing differences in black and white  |
        | ``screenshot_format`` | Image format of screenshots, ``jpg`` or ``png`` |
        | ``DPI`` | Resolution in which documents are rendered before comparison, only relevant for ``pdf``, ``ps`` and ``pcl``. Images will be compared in their original resolution |
        | ``watermark_file`` | Path to an image/document or a folder containing multiple images. They shall only contain a ```solid black`` area of the parts that shall be ignored for doc comparisons |
        | ``ocr_engine`` | Use ``tesseract`` or ``east`` for Text Detection and OCR |
        | ``threshold`` | Threshold for doc comparison between 0.0000 and 1.0000 . Default is 0.0000. Higher values mean more tolerance for doc differences. |
        | ``movement_detection`` | Relevant when using ``move_tolerance`` option in ``Compare Images``. Possible options are ``classic``, ``template`` and ``orb``. They use different ways of identifying a moved object/section between two images |
        | ``**kwargs`` | Everything else |

        Those arguments will be taken as default, but some can be overwritten in the keywords.
        """

        self.threshold = threshold
        self.DPI = int(dpi)
        self.DPI_on_lib_init = int(dpi)
        self.take_screenshots = bool(take_screenshots)
        self.show_diff = bool(show_diff)
        self.ocr_engine = ocr_engine
        self.movement_detection = movement_detection
        self.watermark_file = watermark_file
        self.screenshot_format = screenshot_format
        try:
            self.screenshot_dir = Path(screenshot_dir)
        except TypeError:
            self.screenshot_dir = Path.cwd() / Path("screenshots/")
        if not (self.screenshot_format == 'jpg' or self.screenshot_format == 'png'):
            self.screenshot_format = 'jpg'

        self._is_different = False

    @property
    def is_different(self):
        return self._is_different

    @staticmethod
    def generate_mask(reference_image: str, mask_images: Union[str, List[str]], threshold=THRESHOLD):
        """Generate mask base on ``reference_image`` and ``test_image``

        Result is a json for mask when matched success, otherwise None

        | =Arguments= | =Description= |
        | ``reference_image`` | Path or URL of the Reference Image/Document, your expected result. May be .pdf, .ps, .pcl or image files |
        | ``mask_images`` | List of the path or URL of the Reference Image/Document, your expected result. May be .pdf, .ps, .pcl or image files |
        | ``threshold`` | Threshold for doc comparison between 0.0000 and 1.0000 . Default is 0.95. Higher values means that the documents are more similar. |

        Return Examples:
        | [{'type': 'coordinates', 'page': 'all', 'x': 724, 'y': 341, 'width': 139, 'height': 44}]
        | None

        """
        from visual_compare.doc.image.image import MatchImg

        mask = []
        if isinstance(mask_images, str):
            mask_images = [mask_images]
        m_img = MatchImg(threshold=threshold)
        for mi in mask_images:
            res = m_img.parse_mask(source=reference_image, temp=mi)
            mask.extend(res)

        return mask if len(mask) > 0 else None

    def compare_images(self, reference_image: str, test_image: str, placeholder_file: Union[str, list] = None,
                       mask: Union[str, dict, list] = None, check_text_content: bool = False,
                       move_tolerance: int = None, contains_barcodes: bool = False, get_pdf_content: bool = False,
                       force_ocr: bool = False, dpi: int = None, watermark_file: str = None,
                       ignore_watermarks: bool = None, ocr_engine: str = None, resize_candidate: bool = False,
                       blur: bool = False, threshold: float = None, **kwargs):
        """Compares the documents/images ``reference_image`` and ``test_image``.

        Result is passed if no doc differences are detected.

        | =Arguments= | =Description= |
        | ``reference_image`` | Path or URL of the Reference Image/Document, your expected result. May be .pdf, .ps, .pcl or image files |
        | ``test_image`` | Path or URL of the Candidate Image/Document, that's the one you want to test. May be .pdf, .ps, .pcl or image files |
        | ``placeholder_file`` | Path to a ``.json`` which defines areas that shall be ignored for comparison. Those parts will be replaced with solid placeholders  |
        | ``mask`` | Same purpose as ``placeholder_file`` but instead of a file path, this is either ``json`` , a ``dict`` , a ``list`` or a ``string`` which defines the areas to be ignored  |
        | ``check_text_content`` | In case of doc differences: Is it acceptable, if only the text content in the different areas is equal |
        | ``move_tolerance`` | In case of doc differences: Is is acceptable, if only parts in the different areas are moved by ``move_tolerance`` pixels  |
        | ``contains_barcodes`` | Shall the image be scanned for barcodes and shall their content be checked (currently only data matrices are supported) |
        | ``get_pdf_content`` | Only relevant in case of using ``move_tolerance`` and ``check_text_content``: Shall the PDF Content like Texts and Boxes be used for calculations |
        | ``force_ocr`` | Always use OCR to find Texts in Images, even for PDF Documents |
        | ``dpi`` | Resolution in which documents are rendered before comparison |
        | ``watermark_file`` | Path to an image/document or a folder containing multiple images. They shall only contain a ```solid black`` area of the parts that shall be ignored for doc comparisons |
        | ``ignore_watermarks`` | Ignores a very special watermark in the middle of the document |
        | ``ocr_engine`` | Use ``tesseract`` or ``east`` for Text Detection and OCR |
        | ``resize_candidate`` | Allow doc comparison, even of documents have different sizes |
        | ``blur`` | Blur the image before comparison to reduce doc difference caused by noise |
        | ``threshold`` | Threshold for doc comparison between 0.0000 and 1.0000 . Default is 0.0000. Higher values mean more tolerance for doc differences. |
        | ``**kwargs`` | Everything else |

        Special Examples with ``mask``:
        | mask={"page": "all", type: "coordinates", "x": 0, "y": 0, "width": 100, "height": 100}

        """

        reference_collection = []
        compare_collection = []
        detected_differences = []
        screenshot_names = []

        if dpi is None:
            self.DPI = self.DPI_on_lib_init
        else:
            self.DPI = int(dpi)
        if watermark_file is None:
            watermark_file = self.watermark_file
        if ignore_watermarks is None:
            ignore_watermarks = os.getenv('IGNORE_WATERMARKS', False)
        if ocr_engine is None:
            ocr_engine = self.ocr_engine
        if threshold is None:
            threshold = self.threshold

        if mask:
            threshold = threshold + 0.0001

        compare_options = {'get_pdf_content': get_pdf_content, 'ignore_watermarks': ignore_watermarks,
                           'check_text_content': check_text_content, 'contains_barcodes': contains_barcodes,
                           'force_ocr': force_ocr, 'move_tolerance': move_tolerance, 'watermark_file': watermark_file,
                           'ocr_engine': ocr_engine, 'resize_candidate': resize_candidate, 'blur': blur,
                           'threshold': threshold}

        if (os.path.isfile(reference_image) is False) and (is_url(reference_image) is False):
            raise AssertionError(
                'The reference file does not exist: {}'.format(reference_image))

        if (os.path.isfile(test_image) is False) and (is_url(test_image) is False):
            raise AssertionError(
                'The candidate file does not exist: {}'.format(test_image))

        with futures.ThreadPoolExecutor(max_workers=2) as parallel_executor:
            reference_future = parallel_executor.submit(CompareImage, reference_image,
                                                        placeholder_file=placeholder_file,
                                                        contains_barcodes=contains_barcodes,
                                                        get_pdf_content=get_pdf_content, DPI=self.DPI,
                                                        force_ocr=force_ocr, mask=mask, ocr_engine=ocr_engine)
            candidate_future = parallel_executor.submit(
                CompareImage, test_image, contains_barcodes=contains_barcodes, get_pdf_content=get_pdf_content,
                DPI=self.DPI)
            reference_compare_image = reference_future.result()
            candidate_compare_image = candidate_future.result()

        tic = time.perf_counter()
        if reference_compare_image.placeholders:
            candidate_compare_image.placeholders = reference_compare_image.placeholders
            with futures.ThreadPoolExecutor(max_workers=2) as parallel_executor:
                reference_collection_future = parallel_executor.submit(
                    reference_compare_image.get_image_with_placeholders)
                compare_collection_future = parallel_executor.submit(
                    candidate_compare_image.get_image_with_placeholders)
                reference_collection = reference_collection_future.result()
                compare_collection = compare_collection_future.result()
        else:
            reference_collection = reference_compare_image.opencv_images
            compare_collection = candidate_compare_image.opencv_images

        if len(reference_collection) != len(compare_collection):
            logger.warning("Pages in reference file:{}. Pages in candidate file:{}".format(
                len(reference_collection), len(compare_collection)))
            for i in range(len(reference_collection)):
                cv2.putText(reference_collection[i], self.REFERENCE_LABEL, self.BOTTOM_LEFT_CORNER_OF_TEXT,
                            self.FONT, self.FONT_SCALE, self.FONT_COLOR, self.LINE_TYPE)
                self.add_screenshot_to_log(
                    reference_collection[i], "_reference_page_" + str(i + 1))
            for i in range(len(compare_collection)):
                cv2.putText(compare_collection[i], self.CANDIDATE_LABEL, self.BOTTOM_LEFT_CORNER_OF_TEXT,
                            self.FONT, self.FONT_SCALE, self.FONT_COLOR, self.LINE_TYPE)
                self.add_screenshot_to_log(
                    compare_collection[i], "_candidate_page_" + str(i + 1))
            raise AssertionError(
                'Reference File and Candidate File have different number of pages')

        check_difference_results = []
        with futures.ThreadPoolExecutor(max_workers=8) as parallel_executor:
            for i, (reference, candidate) in enumerate(zip(reference_collection, compare_collection)):
                if get_pdf_content:
                    try:
                        reference_pdf_content = reference_compare_image.mu_pdf_doc[i]
                        candidate_pdf_content = candidate_compare_image.mu_pdf_doc[i]
                    except:
                        reference_pdf_content = reference_compare_image.mu_pdf_doc[0]
                        candidate_pdf_content = candidate_compare_image.mu_pdf_doc[0]
                else:
                    reference_pdf_content = None
                    candidate_pdf_content = None
                check_difference_results.append(parallel_executor.submit(
                    self.check_for_differences, reference, candidate, i, detected_differences, screenshot_names,
                    compare_options,
                    reference_pdf_content, candidate_pdf_content))
        for result in check_difference_results:
            if result.exception() is not None:
                raise result.exception()
        if reference_compare_image.barcodes:
            if reference_compare_image.barcodes != candidate_compare_image.barcodes:
                detected_differences.append(True)
                logger.error(
                    f'The barcode content in images is different\nReference image:\n{reference_compare_image.barcodes}\nCandidate image:\n{candidate_compare_image.barcodes}')

        for difference in detected_differences:
            if difference:
                logger.error("The compared images are different")
                reference_compare_image.mu_pdf_doc = None
                candidate_compare_image.mu_pdf_doc = None
                self._is_different = True

        logger.info("The compared images are equal")

        toc = time.perf_counter()
        logger.debug(f"Visual Image comparison performed in {toc - tic:0.4f} seconds")

        return screenshot_names

    @staticmethod
    def get_images_with_highlighted_differences(thresh, reference, candidate, extension=10):

        thresh = cv2.dilate(thresh, None, iterations=extension)
        thresh = cv2.erode(thresh, None, iterations=extension)
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # loop over the contours
        for c in contours:
            # compute the bounding box of the contour and then draw the
            # bounding box on both input images to represent where the two
            # images differ
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(reference, (x, y), (x + w, y + h), (0, 0, 255), 4)
            cv2.rectangle(candidate, (x, y), (x + w, y + h), (0, 0, 255), 4)
        return reference, candidate, contours

    @staticmethod
    def get_diff_rectangle(thresh):
        points = cv2.findNonZero(thresh)
        (x, y, w, h) = cv2.boundingRect(points)
        return x, y, w, h

    def add_screenshot_to_log(self, image, suffix):
        screenshot_name = str(str(uuid.uuid1()) + suffix +
                              '.{}'.format(self.screenshot_format))
        abs_screenshot_path = str(self.screenshot_dir / screenshot_name)
        os.makedirs(os.path.dirname(abs_screenshot_path), exist_ok=True)
        if self.screenshot_format == 'jpg':
            cv2.imwrite(abs_screenshot_path, image, [
                int(cv2.IMWRITE_JPEG_QUALITY), 70])
        else:
            cv2.imwrite(abs_screenshot_path, image)

        return screenshot_name

    def find_partial_image_position(self, img, template, threshold=0.1, detection="classic"):

        if detection == "template":
            result = self.find_partial_image_distance_with_match_template(img, template, threshold)

        elif detection == "classic":
            result = self.find_partial_image_distance_with_classic_method(img, template, threshold)

        elif detection == "orb":
            result = self.find_partial_image_distance_with_orb(img, template)

        return result

    @staticmethod
    def find_partial_image_distance_with_classic_method(img, template, threshold=0.1):
        logger.info("Find partial image position")
        rectangles = []
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        h, w = template.shape[0:2]
        logger.info("Old detection")
        template_blur = cv2.GaussianBlur(template_gray, (3, 3), 0)
        template_thresh = cv2.threshold(
            template_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Obtain bounding rectangle and extract ROI
        temp_x, temp_y, temp_w, temp_h = cv2.boundingRect(template_thresh)

        res = cv2.matchTemplate(
            img_gray, template_gray[temp_y:temp_y + temp_h, temp_x:temp_x + temp_w], cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        res_temp = cv2.matchTemplate(template_gray, template_gray[temp_y:temp_y + temp_h, temp_x:temp_x + temp_w],
                                     cv2.TM_SQDIFF_NORMED)
        min_val_temp, max_val_temp, min_loc_temp, max_loc_temp = cv2.minMaxLoc(
            res_temp)

        if min_val < threshold:
            return {"pt1": min_loc, "pt2": min_loc_temp}
        return

    @staticmethod
    def find_partial_image_distance_with_match_template(img, template, threshold=0.1):
        logger.info("Find partial image position")
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        h, w = template.shape[0:2]
        logger.info("dev detection")
        mask = cv2.absdiff(img_gray, template_gray)
        mask[mask > 0] = 255

        # find contours in the mask and get the largest one
        contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # get largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        contour_mask = np.zeros(mask.shape, np.uint8)
        cv2.drawContours(contour_mask, [largest_contour], -1, 255, -1)

        masked_img = cv2.bitwise_not(cv2.bitwise_and(contour_mask, cv2.bitwise_not(img_gray)))
        masked_template = cv2.bitwise_not(cv2.bitwise_and(contour_mask, cv2.bitwise_not(template_gray)))
        template_blur = cv2.GaussianBlur(masked_template, (3, 3), 0)
        template_thresh = cv2.threshold(
            template_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        temp_x, temp_y, temp_w, temp_h = cv2.boundingRect(template_thresh)
        res = cv2.matchTemplate(
            masked_img, masked_template[temp_y:temp_y + temp_h, temp_x:temp_x + temp_w], cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        res_temp = cv2.matchTemplate(masked_template, masked_template[temp_y:temp_y + temp_h, temp_x:temp_x + temp_w],
                                     cv2.TM_SQDIFF_NORMED)
        min_val_temp, max_val_temp, min_loc_temp, max_loc_temp = cv2.minMaxLoc(
            res_temp)

        if min_val < threshold:
            return {"pt1": min_loc, "pt2": min_loc_temp}
        return

    def get_orb_key_points_and_descriptors(self, img1, img2, edge_threshold=5, patch_size=10):
        orb = cv2.ORB_create(nfeatures=250, edgeThreshold=edge_threshold, patchSize=patch_size)
        img1_kp, img1_des = orb.detectAndCompute(img1, None)
        img2_kp, img2_des = orb.detectAndCompute(img2, None)

        if len(img1_kp) == 0 or len(img2_kp) == 0:
            if patch_size > 4:
                patch_size -= 4
                edge_threshold = int(patch_size / 2)
                return self.get_orb_key_points_and_descriptors(img1, img2, edge_threshold, patch_size)
            else:
                return None, None, None, None

        return img1_kp, img1_des, img2_kp, img2_des

    def find_partial_image_distance_with_orb(self, img, template):
        logger.info("Find partial image position")
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        h, w = template.shape[0:2]
        logger.info("dev detection")
        mask = cv2.absdiff(img_gray, template_gray)
        mask[mask > 0] = 255

        # find contours in the mask and get the largest one
        contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # get largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        contour_mask = np.zeros(mask.shape, np.uint8)

        for cnt in contours:
            cv2.drawContours(contour_mask, [cnt], -1, 255, -1)

        masked_img = cv2.bitwise_not(cv2.bitwise_and(contour_mask, cv2.bitwise_not(img_gray)))
        masked_template = cv2.bitwise_not(cv2.bitwise_and(contour_mask, cv2.bitwise_not(template_gray)))

        edges_img = cv2.Canny(masked_img, 100, 200)
        edges_template = cv2.Canny(masked_template, 100, 200)

        # Find the keypoints and descriptors for the template image
        template_key_points, template_descriptors, target_keypoints, target_descriptors = self.get_orb_key_points_and_descriptors(
            edges_template, edges_img)

        if len(template_key_points) == 0 or len(target_keypoints) == 0:
            return

        # Create a brute-force matcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Match the template image with the target image
        matches = bf.match(template_descriptors, target_descriptors)

        if len(matches) > 0:
            # Sort the matches based on their distance
            matches = sorted(matches, key=lambda x: x.distance)
            best_matches = matches[:10]
            # Estimate the transformation matrix between the two images
            src_pts = np.float32([template_key_points[m.queryIdx].pt for m in best_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([target_keypoints[m.trainIdx].pt for m in best_matches]).reshape(-1, 1, 2)

            m, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # Calculate the amount of movement between the two images
            movement = np.sqrt(np.sum(m[:, 2] ** 2))

            self.add_screenshot_to_log(
                cv2.drawMatches(masked_template, template_key_points, masked_img, target_keypoints, best_matches, None,
                                flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS), "ORB_matches")
            return {"distance": movement}

            # Draw the matches on the target image
            # result = cv2.drawMatches(masked_template, template_keypoints, masked_img, target_keypoints, matches[:10], None, flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)

    @staticmethod
    def overlay_two_images(image, overlay, ignore_color=None):
        if ignore_color is None:
            ignore_color = [255, 255, 255]
        ignore_color = np.asarray(ignore_color)
        mask = ~(overlay == ignore_color).all(-1)
        # Or mask = (overlay!=ignore_color).any(-1)
        out = image.copy()
        out[mask] = image[mask] * 0.5 + overlay[mask] * 0.5
        return out

    def check_for_differences(self, reference, candidate, i, detected_differences, screenshot_names, compare_options,
                              reference_pdf_content=None, candidate_pdf_content=None):

        if reference.shape[0] != candidate.shape[0] or reference.shape[1] != candidate.shape[1]:
            if compare_options['resize_candidate']:
                candidate = cv2.resize(
                    candidate, (reference.shape[1], reference.shape[0]))
            else:
                raise AssertionError(
                    f'The compared images have different dimensions:\nreference:{reference.shape}\ncandidate:{candidate.shape}')

        with futures.ThreadPoolExecutor(max_workers=2) as parallel_executor:
            gray_a_future = parallel_executor.submit(
                cv2.cvtColor, reference, cv2.COLOR_BGR2GRAY)
            gray_b_future = parallel_executor.submit(
                cv2.cvtColor, candidate, cv2.COLOR_BGR2GRAY)
            gray_a = gray_a_future.result()
            gray_b = gray_b_future.result()

        # Blur images if blur=True
        if compare_options['blur']:
            kernel_size = int(gray_a.shape[1] / 50)
            # must be odd if median
            kernel_size += kernel_size % 2 - 1
            gray_a = cv2.GaussianBlur(gray_a, (kernel_size, kernel_size), 1.5)
            gray_b = cv2.GaussianBlur(gray_b, (kernel_size, kernel_size), 1.5)

        if self.take_screenshots:
            # Not necessary to take screenshots for every successful comparison
            self.add_screenshot_to_log(np.concatenate(
                (reference, candidate), axis=1), "_page_" + str(i + 1) + "_compare_concat")

        absolute_diff = cv2.absdiff(gray_a, gray_b)
        # if absolute difference is 0, images are equal
        if np.sum(absolute_diff) == 0:
            return

        # compute the Structural Similarity Index (SSIM) between the two
        # images, ensuring that the difference image is returned
        (score, diff) = metrics.structural_similarity(
            gray_a, gray_b, gaussian_weights=True, full=True)
        score = abs(1 - score)

        if score > compare_options['threshold']:

            diff = (diff * 255).astype("uint8")

            thresh = cv2.threshold(diff, 0, 255,
                                   cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            reference_with_rect, candidate_with_rect, contours = self.get_images_with_highlighted_differences(
                thresh, reference.copy(), candidate.copy(), extension=int(os.getenv('EXTENSION', 2)))

            cv2.putText(reference_with_rect, self.REFERENCE_LABEL, self.BOTTOM_LEFT_CORNER_OF_TEXT,
                        self.FONT, self.FONT_SCALE, self.FONT_COLOR, self.LINE_TYPE)
            cv2.putText(candidate_with_rect, self.CANDIDATE_LABEL, self.BOTTOM_LEFT_CORNER_OF_TEXT,
                        self.FONT, self.FONT_SCALE, self.FONT_COLOR, self.LINE_TYPE)

            screenshot_name = self.add_screenshot_to_log(np.concatenate(
                (reference_with_rect, candidate_with_rect), axis=1), "_page_" + str(i + 1) + "_rectangles_concat")
            screenshot_names.append(screenshot_name)

            if self.show_diff:
                self.add_screenshot_to_log(np.concatenate(
                    (diff, thresh), axis=1), "_page_" + str(i + 1) + "_diff")

            images_are_equal = False

            if (compare_options["ignore_watermarks"] is True and len(contours) == 1) or compare_options[
                "watermark_file"] is not None:
                if compare_options["ignore_watermarks"] is True and len(contours) == 1:
                    (x, y, w, h) = cv2.boundingRect(contours[0])
                    diff_center_x = abs((x + w / 2) - (reference.shape[1] / 2))
                    diff_center_y = abs((y + h / 2) - (reference.shape[0] / 2))
                    if (diff_center_x < reference.shape[1] * self.WATERMARK_CENTER_OFFSET) and (
                            w * 25.4 / self.DPI < self.WATERMARK_WIDTH) and (
                            h * 25.4 / self.DPI < self.WATERMARK_HEIGHT):
                        images_are_equal = True
                        logger.info(
                            "A watermark position was identified. After ignoring watermark area, both images are equal")
                        return
                if compare_options["watermark_file"] is not None:
                    watermark_file = compare_options["watermark_file"]
                    if isinstance(watermark_file, str):
                        if os.path.isdir(watermark_file):
                            watermark_file = [str(os.path.join(watermark_file, f)) for f in os.listdir(
                                watermark_file) if os.path.isfile(os.path.join(watermark_file, f))]
                        else:
                            watermark_file = [watermark_file]
                    if isinstance(watermark_file, list):
                        try:
                            for single_watermark in watermark_file:
                                try:
                                    watermark = CompareImage(
                                        single_watermark, DPI=self.DPI).opencv_images[0]
                                except:
                                    logger.error(
                                        f'Watermark file {single_watermark} could not be loaded. Continue with next item.')
                                    continue
                                # Check if alpha channel is present and remove it
                                if watermark.shape[2] == 4:
                                    watermark = watermark[:, :, :3]
                                watermark_gray = cv2.cvtColor(
                                    watermark, cv2.COLOR_BGR2GRAY)
                                # watermark_gray = (watermark_gray * 255).astype("uint8")
                                mask = cv2.threshold(watermark_gray, 10, 255, cv2.THRESH_BINARY)[1]
                                # Check if width or height of mask and reference are not equal
                                if mask.shape[0] != reference.shape[0] or mask.shape[1] != reference.shape[1]:
                                    # Resize mask to match thresh
                                    mask = cv2.resize(mask, (reference.shape[1], reference.shape[0]))

                                mask_inv = cv2.bitwise_not(mask)
                                # dilate the mask to account for slight misalignments
                                mask_inv = cv2.dilate(mask_inv, None, iterations=2)
                                result = cv2.subtract(absolute_diff, mask_inv)
                                if cv2.countNonZero(cv2.subtract(absolute_diff, mask_inv)) == 0 or cv2.countNonZero(
                                        cv2.subtract(thresh, mask_inv)) == 0:
                                    images_are_equal = True
                                    logger.info(
                                        "A watermark file was provided. After removing watermark area, both images are equal")
                                    return
                        except:
                            raise AssertionError(
                                'The provided watermark_file format is invalid. Please provide a path to a file or a list of files.')
                    else:
                        raise AssertionError(
                            'The provided watermark_file format is invalid. Please provide a path to a file or a list of files.')

            if compare_options["check_text_content"] is True and images_are_equal is not True:
                if compare_options["get_pdf_content"] is not True:
                    # x, y, w, h = self.get_diff_rectangle(thresh)
                    images_are_equal = True
                    for c in range(len(contours)):
                        (x, y, w, h) = cv2.boundingRect(contours[c])
                        diff_area_reference = reference[y:y + h, x:x + w]
                        diff_area_candidate = candidate[y:y + h, x:x + w]

                        self.add_screenshot_to_log(
                            diff_area_reference, "_page_" + str(i + 1) + "_diff_area_reference_" + str(c))
                        self.add_screenshot_to_log(
                            diff_area_candidate, "_page_" + str(i + 1) + "_diff_area_test_" + str(c))

                        text_reference = pytesseract.image_to_string(
                            diff_area_reference, config='--psm 6').replace("\n\n", "\n")
                        text_candidate = pytesseract.image_to_string(
                            diff_area_candidate, config='--psm 6').replace("\n\n", "\n")
                        if text_reference.strip() == text_candidate.strip():
                            logger.info("Partial text content is the same")
                            logger.info(text_reference)
                        else:
                            images_are_equal = False
                            detected_differences.append(True)
                            logger.warning("Partial text content is different")
                            logger.warning(text_reference + " is not equal to " + text_candidate)
                elif compare_options["get_pdf_content"] is True:

                    images_are_equal = True
                    ref_words = reference_pdf_content.get_text("words")
                    cand_words = candidate_pdf_content.get_text("words")
                    for c in range(len(contours)):

                        (x, y, w, h) = cv2.boundingRect(contours[c])
                        rect = fitz.Rect(
                            x * 72 / self.DPI, y * 72 / self.DPI, (x + w) * 72 / self.DPI, (y + h) * 72 / self.DPI)
                        diff_area_ref_words = [
                            w for w in ref_words if fitz.Rect(w[:4]).intersects(rect)]
                        diff_area_cand_words = [
                            w for w in cand_words if fitz.Rect(w[:4]).intersects(rect)]
                        diff_area_ref_words = make_text(diff_area_ref_words)
                        diff_area_cand_words = make_text(diff_area_cand_words)
                        diff_area_reference = reference[y:y + h, x:x + w]
                        diff_area_candidate = candidate[y:y + h, x:x + w]

                        self.add_screenshot_to_log(
                            diff_area_reference, "_page_" + str(i + 1) + "_diff_area_reference_" + str(c))
                        self.add_screenshot_to_log(
                            diff_area_candidate, "_page_" + str(i + 1) + "_diff_area_test_" + str(c))

                        if len(diff_area_ref_words) != len(diff_area_cand_words):
                            images_are_equal = False
                            detected_differences.append(True)
                            logger.info("The identified pdf layout elements are different",
                                        diff_area_ref_words, diff_area_cand_words)
                        else:

                            if diff_area_ref_words.strip() != diff_area_cand_words.strip():
                                images_are_equal = False
                                detected_differences.append(True)
                                logger.warning("Partial text content is different")
                                logger.warning(diff_area_ref_words.strip(), " is not equal to ",
                                               diff_area_cand_words.strip())
                        if images_are_equal:
                            logger.info("Partial text content of area is the same")
                            logger.info(diff_area_ref_words)

            if compare_options["move_tolerance"] is not None and images_are_equal is not True:
                move_tolerance = int(compare_options["move_tolerance"])
                images_are_equal = True

                if compare_options["get_pdf_content"] is not True:
                    # Experimental, to solve a problem with small images
                    # wr, hr, _ = reference.shape
                    for c in range(len(contours)):

                        (x, y, w, h) = cv2.boundingRect(contours[c])
                        diff_area_reference = reference[y:y + h, x:x + w]
                        diff_area_candidate = candidate[y:y + h, x:x + w]

                        # Experimental, to solve a problem with small images
                        # search_area_candidate = candidate[(y - self.BORDER_FOR_MOVE_TOLERANCE_CHECK) if y >= self.BORDER_FOR_MOVE_TOLERANCE_CHECK else 0:(y + h + self.BORDER_FOR_MOVE_TOLERANCE_CHECK) if hr >= (y + h + self.BORDER_FOR_MOVE_TOLERANCE_CHECK) else hr, (x - self.BORDER_FOR_MOVE_TOLERANCE_CHECK) if x >= self.BORDER_FOR_MOVE_TOLERANCE_CHECK else 0:(x + w + self.BORDER_FOR_MOVE_TOLERANCE_CHECK) if wr >= (x + w + self.BORDER_FOR_MOVE_TOLERANCE_CHECK) else wr]

                        search_area_candidate = candidate[
                                                y - self.BORDER_FOR_MOVE_TOLERANCE_CHECK:y + h + self.BORDER_FOR_MOVE_TOLERANCE_CHECK,
                                                x - self.BORDER_FOR_MOVE_TOLERANCE_CHECK:x + w + self.BORDER_FOR_MOVE_TOLERANCE_CHECK]
                        search_area_reference = reference[
                                                y - self.BORDER_FOR_MOVE_TOLERANCE_CHECK:y + h + self.BORDER_FOR_MOVE_TOLERANCE_CHECK,
                                                x - self.BORDER_FOR_MOVE_TOLERANCE_CHECK:x + w + self.BORDER_FOR_MOVE_TOLERANCE_CHECK]

                        # self.add_screenshot_to_log(search_area_candidate)
                        # self.add_screenshot_to_log(search_area_reference)
                        # self.add_screenshot_to_log(diff_area_candidate)
                        # self.add_screenshot_to_log(diff_area_reference)
                        try:
                            positions_in_compare_image = self.find_partial_image_position(
                                search_area_candidate, diff_area_reference, detection=self.movement_detection)
                        except:
                            logger.error("Error in finding position in compare image")
                            images_are_equal = False
                            detected_differences.append(True)
                            continue
                        # positions_in_compare_image = self.find_partial_image_position(candidate, diff_area_reference)
                        if (np.mean(diff_area_reference) == 255) or (np.mean(diff_area_candidate) == 255):
                            images_are_equal = False
                            detected_differences.append(True)

                            logger.warning("Image section contains only white background")

                            self.add_screenshot_to_log(np.concatenate((cv2.copyMakeBorder(diff_area_reference, top=2,
                                                                                          bottom=2, left=2, right=2,
                                                                                          borderType=cv2.BORDER_CONSTANT,
                                                                                          value=[
                                                                                              0, 0, 0]),
                                                                       cv2.copyMakeBorder(diff_area_candidate, top=2,
                                                                                          bottom=2, left=2, right=2,
                                                                                          borderType=cv2.BORDER_CONSTANT,
                                                                                          value=[0, 0, 0])), axis=1),
                                                       "_diff_area_concat")

                            # self.add_screenshot_to_log(np.concatenate((diff_area_reference, diff_area_candidate), axis=1), "_diff_area_concat")

                        else:
                            if positions_in_compare_image:
                                # if positions_in_compare_image contains a key 'distance'
                                # then compare if the distance is within the move tolerance
                                if 'distance' in positions_in_compare_image:
                                    move_distance = positions_in_compare_image['distance']
                                    if int(move_distance) > int(move_tolerance):
                                        print("Image section moved ",
                                              move_distance, " pixels")
                                        print(
                                            "This is outside of the allowed range of ", move_tolerance, " pixels")
                                        images_are_equal = False
                                        detected_differences.append(True)
                                        self.add_screenshot_to_log(self.overlay_two_images(
                                            search_area_reference, search_area_candidate), "_diff_area_blended")
                                    else:
                                        print("Image section moved ",
                                              move_distance, " pixels")
                                        print(
                                            "This is within the allowed range of ", move_tolerance, " pixels")
                                        self.add_screenshot_to_log(self.overlay_two_images(
                                            search_area_reference, search_area_candidate), "_diff_area_blended")

                                if 'pt1' in positions_in_compare_image and 'pt2' in positions_in_compare_image:

                                    pt_original = positions_in_compare_image['pt1']
                                    pt_compare = positions_in_compare_image['pt2']
                                    x_moved = abs(pt_original[0] - pt_compare[0])
                                    y_moved = abs(pt_original[1] - pt_compare[1])
                                    move_distance = math.sqrt(
                                        x_moved ** 2 + y_moved ** 2)
                                    # cv2.arrowedLine(candidate_with_rect, pt_original, pt_compare, (255, 0, 0), 4)
                                    if int(move_distance) > int(move_tolerance):
                                        print("Image section moved ",
                                              move_distance, " pixels")
                                        print(
                                            "This is outside of the allowed range of ", move_tolerance, " pixels")
                                        images_are_equal = False
                                        detected_differences.append(True)
                                        self.add_screenshot_to_log(self.overlay_two_images(
                                            search_area_reference, search_area_candidate), "_diff_area_blended")

                                    else:
                                        print("Image section moved ",
                                              move_distance, " pixels")
                                        print(
                                            "This is within the allowed range of ", move_tolerance, " pixels")
                                        self.add_screenshot_to_log(self.overlay_two_images(
                                            search_area_reference, search_area_candidate), "_diff_area_blended")

                            else:
                                images_are_equal = False
                                detected_differences.append(True)
                                print(
                                    "The reference image section was not found in test image (or vice versa)")
                                self.add_screenshot_to_log(np.concatenate((
                                    cv2.copyMakeBorder(diff_area_reference, top=2,
                                                       bottom=2, left=2, right=2,
                                                       borderType=cv2.BORDER_CONSTANT,
                                                       value=[
                                                           0, 0, 0]),
                                    cv2.copyMakeBorder(diff_area_candidate, top=2,
                                                       bottom=2, left=2, right=2,
                                                       borderType=cv2.BORDER_CONSTANT,
                                                       value=[0, 0, 0])), axis=1),
                                    "_diff_area_concat")

                elif compare_options["get_pdf_content"] is True:
                    images_are_equal = True
                    ref_words = reference_pdf_content.get_text("words")
                    cand_words = candidate_pdf_content.get_text("words")
                    for c in range(len(contours)):

                        (x, y, w, h) = cv2.boundingRect(contours[c])
                        rect = fitz.Rect(
                            x * 72 / self.DPI, y * 72 / self.DPI, (x + w) * 72 / self.DPI, (y + h) * 72 / self.DPI)
                        diff_area_ref_words = [
                            w for w in ref_words if fitz.Rect(w[:4]).intersects(rect)]
                        diff_area_cand_words = [
                            w for w in cand_words if fitz.Rect(w[:4]).intersects(rect)]
                        # diff_area_ref_words = make_text(diff_area_ref_words)
                        # diff_area_cand_words = make_text(diff_area_cand_words)
                        diff_area_reference = reference[y:y + h, x:x + w]
                        diff_area_candidate = candidate[y:y + h, x:x + w]
                        self.add_screenshot_to_log(
                            diff_area_reference, "_page_" + str(i + 1) + "_diff_area_reference_" + str(c))
                        self.add_screenshot_to_log(
                            diff_area_candidate, "_page_" + str(i + 1) + "_diff_area_test_" + str(c))

                        if len(diff_area_ref_words) != len(diff_area_cand_words):
                            images_are_equal = False
                            detected_differences.append(True)
                            print("The identified pdf layout elements are different",
                                  diff_area_ref_words, diff_area_cand_words)
                        else:
                            for ref_Item, cand_Item in zip(diff_area_ref_words, diff_area_cand_words):
                                if ref_Item == cand_Item:
                                    pass

                                elif str(ref_Item[4]).strip() == str(cand_Item[4]).strip():
                                    left_moved = abs(
                                        ref_Item[0] - cand_Item[0]) * self.DPI / 72
                                    top_moved = abs(
                                        ref_Item[1] - cand_Item[1]) * self.DPI / 72
                                    right_moved = abs(
                                        ref_Item[2] - cand_Item[2]) * self.DPI / 72
                                    bottom_moved = abs(
                                        ref_Item[3] - cand_Item[3]) * self.DPI / 72
                                    print("Checking pdf elements",
                                          ref_Item, cand_Item)

                                    if int(left_moved) > int(move_tolerance) or int(top_moved) > int(
                                            move_tolerance) or int(right_moved) > int(move_tolerance) or int(
                                        bottom_moved) > int(move_tolerance):
                                        print("Image section moved ", left_moved,
                                              top_moved, right_moved, bottom_moved, " pixels")
                                        print(
                                            "This is outside of the allowed range of ", move_tolerance, " pixels")
                                        images_are_equal = False
                                        detected_differences.append(True)
                                        self.add_screenshot_to_log(self.overlay_two_images(
                                            diff_area_reference, diff_area_candidate), "_diff_area_blended")

                                    else:
                                        print("Image section moved ", left_moved,
                                              top_moved, right_moved, bottom_moved, " pixels")
                                        print(
                                            "This is within the allowed range of ", move_tolerance, " pixels")
                                        self.add_screenshot_to_log(self.overlay_two_images(
                                            diff_area_reference, diff_area_candidate), "_diff_area_blended")
            if images_are_equal is not True:
                detected_differences.append(True)


def make_text(words):
    """Return text string output of get_text("words").
    Word items are sorted for reading sequence left to right,
    top to bottom.
    """
    line_dict = {}  # key: vertical coordinate, value: list of words
    words.sort(key=lambda wo: wo[0])  # sort by horizontal coordinate
    for w in words:  # fill the line dictionary
        y1 = round(w[3], 1)  # bottom of a word: don't be too picky!
        word = w[4]  # the text of the word
        line = line_dict.get(y1, [])  # read current line content
        line.append(word)  # append new word
        line_dict[y1] = line  # write back to dict
    lines = list(line_dict.items())
    lines.sort()  # sort vertically
    return "\n".join([" ".join(line[1]) for line in lines])
