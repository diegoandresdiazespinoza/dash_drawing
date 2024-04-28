import cv2
import numpy as np
from skimage.morphology import skeletonize
from tkinter import Tk, Label, Button, Scale, HORIZONTAL, filedialog, StringVar, OptionMenu
from PIL import Image, ImageTk


def create_dashed_line(img, points, dash_length=20, space_length=10, color=(0, 0, 0), thickness=1):
    accumulated_dist = 0
    start_idx = 0

    for i in range(1, len(points)):
        distance = np.linalg.norm(points[i] - points[i - 1])
        accumulated_dist += distance

        if accumulated_dist >= (dash_length + space_length):
            end_idx = i
            while accumulated_dist >= (dash_length + space_length):
                ratio = dash_length / accumulated_dist
                sub_end_point = points[start_idx] * (1 - ratio) + points[end_idx] * ratio
                cv2.line(img, tuple(points[start_idx].astype(int)), tuple(sub_end_point.astype(int)), color, thickness)
                start_idx = end_idx
                accumulated_dist -= (dash_length + space_length)
                end_idx += 1


def process_image(dash_length, space_length, retrieval_mode, thickness):
    global output_image_label, img, output

    binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)[1]
    skeleton = skeletonize(binary // 255).astype(np.uint8) * 255
    contours, _ = cv2.findContours(skeleton, retrieval_mode, cv2.CHAIN_APPROX_NONE)
    output = np.ones_like(img) * 255  # White background

    for contour in contours:
        points = contour.squeeze()
        if points.ndim == 1:
            points = np.expand_dims(points, axis=0)
        if len(points) > 1:
            create_dashed_line(output, points, dash_length, space_length, thickness=thickness)

    update_output_image()


def update_output_image():
    output_pil = Image.fromarray(output)
    output_photo = ImageTk.PhotoImage(image=output_pil)
    output_image_label.config(image=output_photo)
    output_image_label.image = output_photo


def update_image(val):
    dash_length = dash_scale.get()
    space_length = space_scale.get()
    retrieval_mode = contour_modes[var_mode.get()]
    thickness = thick.get()
    process_image(dash_length, space_length, retrieval_mode, thickness)


def load_image():
    global img
    file_path = filedialog.askopenfilename()
    if file_path:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        input_image = Image.fromarray(img)
        input_photo = ImageTk.PhotoImage(image=input_image)
        input_image_label.config(image=input_photo)
        input_image_label.image = input_photo
        update_image(None)


def save_image():
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg")
    if file_path:
        cv2.imwrite(file_path, output)


# Initialize retrieval modes mapping
contour_modes = {
    "External": cv2.RETR_EXTERNAL,
    "List": cv2.RETR_LIST,
    "Tree": cv2.RETR_TREE
}

# Create the main window
root = Tk()
root.title("Image Processing GUI")

# Initialize empty images
img = np.zeros((300, 300), dtype=np.uint8)
output = img.copy()

# Display the input image
input_image = Image.fromarray(img)
input_photo = ImageTk.PhotoImage(image=input_image)
input_image_label = Label(root, image=input_photo)
input_image_label.pack(side="left")

# Display the output image
output_image = Image.fromarray(output)
output_photo = ImageTk.PhotoImage(image=output_image)
output_image_label = Label(root, image=output_photo)
output_image_label.pack(side="right")

# Dropdown for contour retrieval modes
var_mode = StringVar(root)
var_mode.set("External")  # default value
mode_menu = OptionMenu(root, var_mode, *contour_modes.keys(), command=lambda _: update_image(None))
mode_menu.pack()

# Sliders for dash and space lengths
dash_scale = Scale(root, from_=1, to=50, orient=HORIZONTAL, label="Dash Length", command=update_image)
dash_scale.pack()
space_scale = Scale(root, from_=1, to=50, orient=HORIZONTAL, label="Space Length", command=update_image)
space_scale.pack()
thick = Scale(root, from_=1, to=10, orient=HORIZONTAL, label="Thickness", command=update_image)
thick.pack()

# Buttons to load and save images
load_button = Button(root, text="Load Image", command=load_image)
load_button.pack()
save_button = Button(root, text="Save Image", command=save_image)
save_button.pack()

root.mainloop()
