import cv2
from pytesseract import pytesseract
import openai

# Configure OpenAI API
openai.api_key = "your_openai_api_key"

# Set Tesseract executable path if needed
# pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

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
    query = f"""
    OCR detected text data: {ocr_data}.
    Extracted text: {extracted_text}.
    Context: {context_description}.
    Suggest improvements or preprocessing techniques for better accuracy.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant for image analysis."},
            {"role": "user", "content": query},
        ]
    )
    return response["choices"][0]["message"]["content"]

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
def main():
    # Step 1: Input Screenshot
    screenshot_path = "screen.png"

    # Step 2: Preprocess the Image
    processed_image = preprocess_image(screenshot_path)
    cv2.imwrite("processed_screen.png", processed_image)  # Save for verification

    # Step 3: Perform OCR
    ocr_data, extracted_text = perform_ocr(processed_image)

    # Step 4: Analyze with ChatGPT
    context_description = "Looking for the login button or 'Submit' text in the image."
    chatgpt_response = analyze_with_chatgpt(ocr_data, extracted_text, context_description)
    print("ChatGPT Response:", chatgpt_response)

    # Step 5: Extract Target Coordinates
    target_text = "Submit"  # Specify the text you want to detect
    coordinates = extract_coordinates(ocr_data, target_text)

    if coordinates:
        print(f"Coordinates of '{target_text}': {coordinates}")
        # Use Appium to interact with the element at these coordinates
    else:
        print(f"'{target_text}' not found in the image.")

if __name__ == "__main__":
    main()
