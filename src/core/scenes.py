import os
import base64

folder_path = './src/utils/image_scenes'

def list_scene_image():
    try:
        files = os.listdir(folder_path)
        image_names = [file for file in files if file.endswith('.jpg') or file.endswith('.png')]
        return image_names
    except Exception as e:
        print(f"Error reading folder: {e}")
        return []

def write_base64_to_image(base64_image_string, name_image):
    image_name = f"{name_image}.png"
    image_path = os.path.join(folder_path, image_name)
    base64_image = base64_image_string.split(';base64,').pop()
    
    try:
        with open(image_path, "wb") as image_file:
            image_file.write(base64.b64decode(base64_image))
        is_image_saved(image_name)
    except Exception as e:
        print(f"Error writing image: {e}")
        return str(e)

def is_image_saved(image_name):
    image_path = os.path.join(folder_path, image_name)
    return os.path.exists(image_path)
