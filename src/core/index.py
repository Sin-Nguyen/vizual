import os
import cv2
import base64
import subprocess

result_folder_path = 'src/utils/result/'
image_scene_folder_path = 'src/utils/image_scenes/'

def read_base_image(base64_image_string):
    try:
        return cv2.imdecode(np.frombuffer(base64.b64decode(base64_image_string), np.uint8), cv2.IMREAD_GRAYSCALE)
    except Exception as e:
        print(e)
        return str(e)

def read_template_image(template_image):
    try:
        return cv2.imread(f"{image_scene_folder_path}/{template_image}.png", cv2.IMREAD_GRAYSCALE)
    except Exception as e:
        print(e)
        return str(e)

def count_images():
    try:
        files = os.listdir(result_folder_path)
        image_files = [file for file in files if file.endswith('.png')]
        return len(image_files)
    except Exception as e:
        print(e)
        return 0

def detect_image(base64_image_string, template_image):
    try:
        image = read_base_image(base64_image_string)
        template = read_template_image(template_image)
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        setting_icon_coordinates = {'x': max_loc[0], 'y': max_loc[1]}
        print('Setting icon coordinates: ', setting_icon_coordinates)
        saved_image_path = draw_rectangle(setting_icon_coordinates, image, template)
        return {'x': setting_icon_coordinates['x'], 'y': setting_icon_coordinates['y'], 'saved_image_path': saved_image_path}
    except Exception as e:
        print(e)
        return str(e)

def draw_rectangle(setting_icon_coordinates, image, template):
    try:
        x, y = setting_icon_coordinates['x'], setting_icon_coordinates['y']
        w, h = template.shape[::-1]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        number = count_images() + 1
        save_path = f"{result_folder_path}step_{number}_result.png"
        cv2.imwrite(save_path, image)
        print('result saved at: ', save_path)
        return os.path.basename(save_path)
    except Exception as e:
        print(e)
        return str(e)

def base64_to_image(base64_string, output_path):
    base64_data = base64_string.replace('data:image/png;base64,', '')
    try:
        with open(output_path, "wb") as image_file:
            image_file.write(base64.b64decode(base64_data))
        print(f"Image saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error writing image file: {e}")
        return str(e)

def convert_to_coordinates(coord_str):
    return {key: int(value) for key, value in (pair.split(':') for pair in coord_str.split(','))}

def detect_with_py(input_base64, template_name):
    template_path = f"src/utils/image_scenes/{template_name}.png"
    base64_to_image(input_base64, 'src/utils/input.png')
    try:
        result = subprocess.run(['python3', 'src/core/openCV.py', 'src/utils/input.png', template_path], capture_output=True, text=True)
        if 'Error:' in result.stdout:
            raise Exception(result.stdout)
        coordinates = convert_to_coordinates(result.stdout.strip())
        return coordinates
    except Exception as e:
        print(e)
        return str(e)
