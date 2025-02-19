import cv2
from pytesseract import pytesseract
from openai import OpenAI
from openai_chat_request import get_chat_completion
import sys
import os

# Preprocessing Function
def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # Apply adaptive thresholding for better OCR performance
    processed = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return processed

# OCR Function
def perform_ocr(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    extracted_text = pytesseract.image_to_string(image)
    return data, extracted_text

# ChatGPT Analysis Function
def analyze_with_chatgpt(ocr_data, extracted_text, context_description=""):
   system_message = "As QA engineer, you are an AI assistant for image analysis" 
   query_list = f"OCR detected text data: {ocr_data}. Extracted text: {extracted_text}. Context: {context_description}. Suggest improvements or preprocessing techniques for better accuracy."
   response = get_chat_completion(query_list, system_message)
   return response

# Coordinate Extraction from OCR Data
def extract_coordinates(ocr_data, target_text):
    for i, text in enumerate(ocr_data['text']):
        if target_text.lower() in text.lower():
            # Extract bounding box coordinates
            x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i])
            center_x, center_y = x + w // 2, y + h // 2
            return center_x, center_y
    return None

# Main Workflow
def main(detection_type, screenshot_path, scene_text):
    # Step 1: Load the Screenshot
    # Step 2: Preprocess the Image
    processed_image = preprocess_image(screenshot_path)
    cv2.imwrite("processed_screen.png", processed_image)  # Save for verification

    # Step 3: Perform OCR
    ocr_data, extracted_text = perform_ocr(processed_image)

    # Step 4: Analyze with ChatGPT
    context_description = "Looking for the {scene_text} text in the image."
    chatgpt_response = analyze_with_chatgpt(ocr_data, extracted_text, context_description)
    print("ChatGPT Response:", chatgpt_response)

    # Step 5: Extract Target Coordinates
    target_text = scene_text  # Specify the text you want to detect
    coordinates = extract_coordinates(ocr_data, target_text)
    if coordinates:
        print(f"Coordinates of '{target_text}': {coordinates}")

        # Draw a red box around the detected text
        x, y = coordinates
        w, h = 100, 50  # Assuming a fixed width and height for the box
        boxed_image = cv2.rectangle(processed_image.copy(), (x - w // 2, y - h // 2), (x + w // 2, y + h // 2), (0, 0, 255), 2)

        # Save the image with the red box
        result_dir = "src/utils/result"
        os.makedirs(result_dir, exist_ok=True)

        # Find the next available number for the result image
        existing_files = os.listdir(result_dir)
        numbers = [int(f.split('_')[1].split('.')[0]) for f in existing_files if f.startswith('result_') and f.endswith('.png')]
        next_number = max(numbers, default=0) + 1

        result_path = os.path.join(result_dir, f"result_{next_number}.png")
        cv2.imwrite(result_path, boxed_image)
        print(f"Result image saved to {result_path}")
        return coordinates
    else:
        return '{target_text} not found in the image'

if __name__ == "__main__":
    main()
