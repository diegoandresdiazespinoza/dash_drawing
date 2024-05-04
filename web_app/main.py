import json

from flask import Flask, render_template, request, jsonify, url_for
from skimage.morphology import skeletonize
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from werkzeug.datastructures import FileStorage

app = Flask(__name__)


def create_dashed_line(img, points, dash_length=20, space_length=10, color=(0, 0, 0)):
    thickness = 1  # Line thickness
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


@app.route('/', methods=['GET', 'POST'])
def index():
    default_image = 'web_app/static/default.png'
    processed_image = json.loads(process(default_image).get_data())["image"]
    print(processed_image)
    return render_template('index.html', default_image=f'/static/default.png',
                           processed_image=f'{processed_image}')

    # return render_template('index.html')

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')  # Remove the '#' symbol if it's there
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


@app.route('/process', methods=['POST'])
def process(_default_image=None):
    if _default_image is not None:
        file = _default_image
    elif "file" in request.form:
        file = request.form.get("file")
    else:
        file = request.files.get('file')
        # Use .get to avoid KeyError
    dash_length = int(request.form.get('dash_length', 20))
    space_length = int(request.form.get('space_length', 10))
    line_color = hex_to_rgb(request.form.get('line_color', '#000000'))

    if not file:
        return jsonify({'error': 'No file provided'})

    if file:
        img = np.array(Image.open(file).convert('L'))
        img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)[1]
        skeleton = skeletonize(binary // 255).astype(np.uint8) * 255
        contours, _ = cv2.findContours(skeleton, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        output = np.ones_like(img_color) * 255  # White background

        for contour in contours:
            points = contour.squeeze()
            if points.ndim == 1:
                points = np.expand_dims(points, axis=0)
            if len(points) > 1:
                create_dashed_line(output, points, dash_length, space_length, line_color)

        img_io = BytesIO()
        Image.fromarray(output).save(img_io, 'PNG')
        img_io.seek(0)
        base64_img = base64.b64encode(img_io.getvalue()).decode('utf-8')
        print("ok")
        return jsonify({'image': 'data:image/png;base64,' + base64_img})
    return jsonify({'error': 'No file provided'})


if __name__ == '__main__':
    app.run(debug=True)
