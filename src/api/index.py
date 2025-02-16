from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from core.index import detect_image, detect_with_py
from core.scenes import list_scene_image, write_base64_to_image
from core.tesseract import detect_text, get_words_dom
from core.analyze_with_gpt import main as analyze_with_gpt
import os
import base64
import logging

app = Flask(__name__)
port = 4721
debug_port = 4900
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB limit

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request_info():
    app.logger.info('Endpoint: %s', request.endpoint)
    # app.logger.info('Body: %s', request.get_data())

@app.route('/', methods=['GET'])
def home():
    return 'OpenCV still alive!', 200

@app.route('/detect/image', methods=['POST'])
def detect_image_route():
    if 'image' not in request.files:
        return jsonify(message='Error: No file part'), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify(message='Error: No selected file'), 400

    try:
        image_base64 = base64.b64encode(file.read()).decode('utf-8')
        scene_option = request.args.get('scene_option')
        detect_option = request.args.get('detect_option')
        coordinates = None

        if detect_option == 'icon':
            coordinates = detect_image(image_base64, scene_option)
        elif detect_option == 'text':
            contrast = request.args.get('contrast')
            option_compare = request.args.get('option_compare')
            threshold = request.args.get('threshold')
            if threshold:
                threshold = list(map(int, threshold.split(',')))
            coordinates = detect_text(image_base64, scene_option, option_compare, contrast, threshold)

        if isinstance(coordinates, Exception):
            return jsonify(message=str(coordinates)), 500

        return jsonify(
            message='Success',
            bestThreshold=coordinates.bestThreshold,
            resultImageName=coordinates.savedImagePath,
            coordinates={'x': coordinates.x, 'y': coordinates.y}
        )
    except Exception as e:
        return jsonify(message=f'Error: {str(e)}'), 500

@app.route('/scene/list', methods=['GET'])
def list_scene_images():
    try:
        image_names = list_scene_image()
        return jsonify(message='Success', images=image_names)
    except Exception as e:
        return jsonify(message=f'Error: {str(e)}'), 500

@app.route('/download/<image_name>', methods=['GET'])
def download_image(image_name):
    image_path = os.path.join('src/utils/result', image_name)
    if os.path.exists(image_path):
        return send_from_directory('src/utils/result', image_name)
    else:
        return jsonify(message=f'Error: not found image with name {image_name} in folder'), 500

@app.route('/scene/upload', methods=['POST'])
def upload_scene_image():
    if 'image' not in request.files:
        return jsonify(message='Error: No file part'), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify(message='Error: No selected file'), 400

    try:
        image_base64 = base64.b64encode(file.read()).decode('utf-8')
        image_name = request.args.get('image_name')
        response = write_base64_to_image(image_base64, image_name)
        if isinstance(response, Exception):
            return jsonify(message=str(response)), 500

        return jsonify(
            message='Upload successfully',
            scene_image_path=f'src/utils/image_scenes/{image_name}.png'
        )
    except Exception as e:
        return jsonify(message=f'Error: {str(e)}'), 500

@app.route('/detect/text/tree', methods=['POST'])
def detect_text_tree():
    if 'image' not in request.files:
        return jsonify(message='Error: No file part'), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify(message='Error: No selected file'), 400

    try:
        image_base64 = base64.b64encode(file.read()).decode('utf-8')
        contrast = request.args.get('contrast')
        threshold = request.args.get('threshold')
        lines = get_words_dom(image_base64, contrast, threshold)

        if isinstance(lines, Exception) or 'Errors' in lines.get('message', ''):
            return jsonify(message=lines.message), 500

        return jsonify(message='Success', lines=lines)
    except Exception as e:
        return jsonify(message=f'Error: {str(e)}'), 500

@app.route('/py/detect/image', methods=['POST'])
def py_detect_image():
    if 'image' not in request.files:
        return jsonify(message='Error: No file part'), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify(message='Error: No selected file'), 400

    try:
        input_base64 = base64.b64encode(file.read()).decode('utf-8')
        scene_option = request.args.get('nameTemplate')
        coordinates = detect_with_py(input_base64, scene_option)

        return jsonify(
            message='Success',
            coordinates={'x': coordinates.x, 'y': coordinates.y}
        )
    except Exception as e:
        return jsonify(message=f'Error: {str(e)}'), 500
    
@app.route('/analyze/text', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    detect_option = request.args.get('detect_option')
    scene_text = request.args.get('scene_text')
    
    image = request.files['image']
    image_path = os.path.join('/tmp', image.filename)
    image.save(image_path)
    
    try:
        result = analyze_with_gpt(detect_option, image_path, scene_text)
        return jsonify({"result": result}), 200
    finally:
        os.remove(image_path)

if __name__ == '__main__':
    app.run(port=port, debug=True)
    # app.run(port=debug_port)
