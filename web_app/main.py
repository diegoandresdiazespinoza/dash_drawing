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
    default_image = 'static/default.png'
    processed_image = json.loads(path_numbers(default_image).get_data())["image"]
    print(processed_image)
    return render_template('index.html', default_image=f'static/default.png',
                           processed_image=f'{processed_image}')

    # return render_template('index.html')

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')  # Remove the '#' symbol if it's there
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

@app.route('/process_path_numbers', methods=['GET', 'POST'])
def path_numbers(_default_image=None):
    if _default_image is not None:
        file = _default_image
    elif "file" in request.form:
        file = request.form.get("file")
    else:
        file = request.files.get('file')

    dash_length = int(request.form.get('dash_length', 5))
    space_length = int(request.form.get('space_length', 10))
    line_color = hex_to_rgb(request.form.get('line_color', '#000000'))
    thickness = 1

    if not file:
        return jsonify({'error': 'No file provided'})



    if file:
        contours, base_image = get_contours(file)
        max_area = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if max_area is None or area > max_area:
                valid_contour = contour
                max_area = area
        output = np.ones_like(base_image) * 255  # White background
        number = 1
        max_contours = 12
        actual_contour = 1
        min_contour_area = 100000
        print(f"Total contours: {len(contours)}")
        points_added = set()
        thresh = 100000
        #contours = [valid_contour]
        for contour in contours:
            #print(f"Area of contour {cv2.contourArea(contour)}")
            accumulated_dist = 0
            start_idx = 0
            points = contour.squeeze()
            contour_area = cv2.contourArea(contour)
            if contour_area <= 0:
                continue
            if contour_area < max_area - thresh or contour_area > max_area + thresh:
                intersection = False
                print(f"Out of area {contour_area}")
                cv2.drawContours(output, contour, -1, (0, 255, 0), 1)
                continue
            else:
                function = "text"

            number = 1
            #print(f"Area in {contour_area}")
            #if actual_contour >= max_contours:
            #    break
            #actual_contour = actual_contour + 1
            if points.ndim == 1:
                #points = np.expand_dims(points, axis=0)
                continue
            if len(points) > 1:
                print(f"Area in contour {cv2.contourArea(contour)}")
                for i in range(1, len(points)):
                    distance = np.linalg.norm(points[i] - points[i - 1])
                    accumulated_dist += distance

                    if accumulated_dist >= (dash_length + space_length):
                        end_idx = i
                        while accumulated_dist >= (dash_length + space_length):
                            ratio = dash_length / accumulated_dist
                            sub_end_point = points[start_idx] * (1 - ratio) + points[end_idx] * ratio
                            cv2.putText(output, str(number), tuple(points[start_idx].astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255))
                            number = number + 1

                            # elif function == "points":
                            #     cv2.drawMarker(output,tuple(points[start_idx].astype(int)),(0,255,0), markerType=cv2.MARKER_SQUARE, markerSize=2, thickness=1 )
                            #         #output, str(number), tuple(points[start_idx].astype(int)), cv2.FONT_HERSHEY_SIMPLEX,
                            #         #0.2, (0, 0, 255))
                            #     number = number + 1
                            #print(points[start_idx])
                            #print(number)
                            points_added.add(str(points[start_idx].astype(str)))
                            start_idx = end_idx
                            accumulated_dist -= (dash_length + space_length)
                            end_idx += 1
        img_io = BytesIO()
        Image.fromarray(output).save(img_io, 'PNG')
        img_io.seek(0)
        base64_img = base64.b64encode(img_io.getvalue()).decode('utf-8')
        print("ok")
        return jsonify({'image': 'data:image/png;base64,' + base64_img})
    return jsonify({'error': 'No file provided'})

@app.route('/process', methods=['POST'])
def process(_default_image=None):
    if _default_image is not None:
        file = _default_image
    elif "file" in request.form:
        file = request.form.get("file")
    else:
        file = request.files.get('file')
        # Use .get to avoid KeyError
    dash_length = int(request.form.get('dash_length', 2))
    space_length = int(request.form.get('space_length', 5))
    line_color = hex_to_rgb(request.form.get('line_color', '#000000'))

    if not file:
        return jsonify({'error': 'No file provided'})

    if file:
        contours, img_color = get_contours(file)
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


def get_contours(file):
    img = np.array(Image.open(file).convert('L'))
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    binary = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)[1]
    skeleton = skeletonize(binary // 255).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    return contours, img_color


if __name__ == '__main__':
    app.run(debug=False, port=5003, host="0.0.0.0")
