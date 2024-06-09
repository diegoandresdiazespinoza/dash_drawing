import cv2
import numpy as np
from tkinter import Tk, filedialog, Button, Label
from PIL import Image, ImageTk


def select_image():
    global panel, output_image
    path = filedialog.askopenfilename()

    if len(path) > 0:
        image = cv2.imread(path)
        output_image = process_image(image)

        # Convert the images to PIL format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        output_image_display = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
        output_image_display = Image.fromarray(output_image_display)
        output_image_display = ImageTk.PhotoImage(output_image_display)

        if panel is None:
            panel = Label(image=image)
            panel.image = image
            panel.pack(side="left", padx=10, pady=10)

            panel_output = Label(image=output_image_display)
            panel_output.image = output_image_display
            panel_output.pack(side="right", padx=10, pady=10)
        else:
            panel.configure(image=image)
            panel.image = image

            panel_output.configure(image=output_image_display)
            panel_output.image = output_image_display


def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output_image = image.copy()

    for i, contour in enumerate(contours):
        #cv2.drawContours(output_image, [contour], -1, (0, 255, 0), 2)
        moments = cv2.moments(contour)
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
            cv2.putText(output_image, str(i + 1), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return output_image


def save_output_image():
    if output_image is not None:
        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if output_path:
            cv2.imwrite(output_path, output_image)



output_image = None
panel = None

root = Tk()
root.title("Contour Numbering")

btn = Button(root, text="Select an Image", command=select_image)
btn.pack(side="top", fill="both", expand="yes", padx="10", pady="10")

btn_save = Button(root, text="Save Output Image", command=save_output_image)
btn_save.pack(side="top", fill="both", expand="yes", padx="10", pady="10")

root.mainloop()

