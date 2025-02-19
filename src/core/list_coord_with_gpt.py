import cv2
import os
import xml.dom.minidom as minidom
import base64
from openai_chat_request import get_chat_completion

def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    processed = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return processed

def resize_image(image_path, max_width=1024):
    """ Resize image to fit within max_width while maintaining aspect ratio. """
    image = cv2.imread(image_path)
    h, w = image.shape[:2]

    if w > max_width:
        scale = max_width / w
        new_size = (int(w * scale), int(h * scale))
        resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        cv2.imwrite(image_path, resized_image)
        print(f"Image resized to {new_size}")

    return image_path

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def detect_text_with_gpt(image_path):
    image_base64 = encode_image_to_base64(image_path)
    
    system_message="You are a helpful AI that detects text in images and provides bounding box coordinates."
    messages=f"Detect words in the image and provide bounding box coordinates visibility. Image: {image_base64}"
    
    response = get_chat_completion(messages, system_message)
    return response.choices[0].message.content

def save_coordinates_to_xml(screen_name, detected_texts):
    doc = minidom.Document()
    root = doc.createElement("OCRData")
    doc.appendChild(root)

    for item in detected_texts:
        text_element = doc.createElement("Text")
        text_element.setAttribute("value", item['text'])
        text_element.setAttribute("x", str(item['bbox'][0]))
        text_element.setAttribute("y", str(item['bbox'][1]))
        text_element.setAttribute("width", str(item['bbox'][2]))
        text_element.setAttribute("height", str(item['bbox'][3]))
        root.appendChild(text_element)

    xml_str = doc.toprettyxml(indent="  ")
    xml_filename = f"{screen_name}.xml"
    with open(xml_filename, "w", encoding="utf-8") as f:
        f.write(xml_str)
    print(f"OCR coordinates saved to {xml_filename}")

def draw_boxes(image, detected_texts):
    for item in detected_texts:
        x, y, w, h = item['bbox']
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green box
    return image

def main(screenshot_path):
    screenshot_path = resize_image(screenshot_path)  # Resize before processing
    screen_name = os.path.splitext(os.path.basename(screenshot_path))[0]
    processed_image = preprocess_image(screenshot_path)
    detected_texts = detect_text_with_gpt(screenshot_path)
    save_coordinates_to_xml(screen_name, detected_texts)
    boxed_image = draw_boxes(processed_image.copy(), detected_texts)

    result_dir = "src/utils/result"
    os.makedirs(result_dir, exist_ok=True)
    result_path = os.path.join(result_dir, f"{screen_name}_result.png")
    cv2.imwrite(result_path, boxed_image)
    print(f"Result image saved to {result_path}")
    return detected_texts

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py <screenshot_path>")
    else:
        main(sys.argv[1])
