import os
import cv2
import numpy as np

result_folder_path = 'src/utils/result/'
image_scene_folder_path = 'src/utils/image_scenes'

def count_images():
    try:
        files = os.listdir(result_folder_path)
        image_files = [file for file in files if file.endswith('.png')]
        return len(image_files)
    except Exception as error:
        print(error)
        return 0

def draw_rectangle(coor, image_base64, image_path='src/utils/result'):
    try:
        image = read_base_image(image_base64)
        # Draw a red rectangle around the setting icon coordinates
        red_color = (0, 0, 255)
        cv2.rectangle(image, (coor['x0'], coor['y0']), (coor['x1'], coor['y1']), red_color, 2)

        # Save the screenshot image
        count_image = count_images() + 1
        save_path = f"{image_path}/step_{count_image}_result.png"
        cv2.imwrite(save_path, image)

        print('result saved at:', save_path)
        last_name = os.path.basename(save_path)
        return last_name
    except Exception as error:
        print(error)
        return Exception('OpenCV Error: Cannot draw in folder')

def read_base_image(base64_image_string):
    try:
        image_data = np.frombuffer(base64.b64decode(base64_image_string), np.uint8)
        return cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    except Exception as error:
        print(error)
        return Exception('OpenCV Error: Cannot read base64 image')

def read_template_image(template_image):
    try:
        return cv2.imread(f"{image_scene_folder_path}/{template_image}.png")
    except Exception as error:
        print(error)
        return Exception(f"OpenCV Error: Not found scene image with name {template_image}.png in folder")
