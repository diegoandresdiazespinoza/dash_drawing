import cv2
import numpy as np
from skimage.morphology import skeletonize


def create_dashed_line(img, points, dash_length=20, space_length=10, color=(0, 0, 0), thickness=1):
    # Draw dashed lines by accumulating distance until a dash can be drawn
    accumulated_dist = 0
    start_idx = 0

    for i in range(1, len(points)):
        distance = np.linalg.norm(points[i] - points[i - 1])
        accumulated_dist += distance

        if accumulated_dist >= (dash_length + space_length):
            end_idx = i
            # Interpolate points to draw dashes
            while accumulated_dist >= (dash_length + space_length):
                ratio = dash_length / accumulated_dist
                sub_end_point = points[start_idx] * (1 - ratio) + points[end_idx] * ratio
                cv2.line(img, tuple(points[start_idx].astype(int)), tuple(sub_end_point.astype(int)), color, thickness)
                start_idx = end_idx
                accumulated_dist -= (dash_length + space_length)
                end_idx += 1


def process_image(input_path, output_path):
    # Load image
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)

    # Skeletonization
    binary = binary.astype(np.uint8)
    skeleton = skeletonize(binary // 255).astype(np.uint8) * 255

    # Find contours on the skeleton
    contours, _ = cv2.findContours(skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Prepare the output image
    output = np.ones_like(img) * 255  # White background

    # Draw dashed lines
    for contour in contours:
        points = contour.squeeze()
        if points.ndim == 1:  # Handle special case of single point contour
            points = np.expand_dims(points, axis=0)
        if len(points) > 1:
            create_dashed_line(output, points, dash_length=5, space_length=10)

    # Save output image
    cv2.imwrite(output_path, output)


# Example usage
process_image('base_1.png', 'output.jpg')
