import cv2
import numpy as np


def draw_dashed_line(img, contour, dash_length=5, space_length=10):
    # Approximate the contour to a polyline
    epsilon = 0.0002 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # Draw dashed line
    for i in range(len(approx) - 1):
        x1, y1 = approx[i][0]
        x2, y2 = approx[i + 1][0]
        length = np.hypot(x2 - x1, y2 - y1)
        num_dashes = int(length / (dash_length + space_length))
        for j in range(num_dashes):
            start = j * (dash_length + space_length)
            end = start + dash_length
            sub_start = start / length
            sub_end = end / length
            sub_x1 = x1 + sub_start * (x2 - x1)
            sub_y1 = y1 + sub_start * (y2 - y1)
            sub_x2 = x1 + sub_end * (x2 - x1)
            sub_y2 = y1 + sub_end * (y2 - y1)
            cv2.line(img, (int(sub_x1), int(sub_y1)), (int(sub_x2), int(sub_y2)), (0, 0, 0), 2)


def process_image(input_path, output_path):
    # Load image
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Binary threshold
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create output image
    output = np.ones_like(img) * 255  # white background

    # Draw dashed lines for each contour
    for contour in contours:
        draw_dashed_line(output, contour)

    # Save output image
    cv2.imwrite(output_path, output)


# Example usage
process_image('base_3.png', 'output.jpg')
