import cv2
import numpy as np
from tkinter import Tk, filedialog
from PIL import Image
import sys

# Function to convert image to pure black and white
def convert_to_black_and_white(image_cv):
    if len(image_cv.shape) == 3:  # Check if the image is colored
        gray_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image_cv  # Image is already in grayscale
    _, bw_image = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY)
    return bw_image

# Function to smooth the image
def smooth_image(image_cv):
    smoothed_image = cv2.GaussianBlur(image_cv, (5, 5), 0)
    return smoothed_image

# Function to double the resolution while maintaining aspect ratio
def double_resolution(image_cv):
    original_height, original_width = image_cv.shape[:2]
    new_width = original_width * 2
    new_height = original_height * 2
    scaled_image = cv2.resize(image_cv, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    return scaled_image

# Main function to process the selected image
def main():
    # Hide the root Tkinter window
    root = Tk()
    root.withdraw()

    # Open file dialog to select an image file
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not file_path:
        print("No file selected.")
        sys.exit()

    # Load the selected image using OpenCV
    image_cv = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if image_cv is None:
        print("Failed to load the image.")
        sys.exit()

    # Double the resolution while maintaining aspect ratio
    scaled_image = double_resolution(image_cv)

    # Convert to pure black and white
    bw_image = convert_to_black_and_white(scaled_image)

    # Smooth the black and white image
    smoothed_bw_image = smooth_image(bw_image)

    # Save the processed image
    output_path = file_path.rsplit(".", 1)[0] + "_processed.png"
    cv2.imwrite(output_path, smoothed_bw_image)

    print(f"Processed image saved to: {output_path}")

if __name__ == "__main__":
    main()
