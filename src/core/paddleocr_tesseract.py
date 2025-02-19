import cv2
import easyocr
import json
import numpy as np
from langdetect import detect

def preprocess_image(image_path):
    """Loads and processes the image for OCR."""
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    return image

def extract_structured_data(image_path):
    """Extracts structured text data and saves an annotated image."""
    try:
        image = preprocess_image(image_path)
        reader = easyocr.Reader(['en', 'vi'])  # English and Vietnamese languages
        results = reader.readtext(image_path)
        
        if not results:
            raise ValueError("No text detected in the image.")
        
        extracted_text = " ".join([res[1] for res in results if res[1].strip()])
        detected_language = detect(extracted_text) if extracted_text else "unknown"
        
        boxes = []
        for res in results:
            text, confidence = res[1], res[2]
            (x_min, y_min), (x_max, y_max) = res[0][0], res[0][2]
            element = {
                "text": text,
                "x": int(x_min),
                "y": int(y_min),
                "width": int(x_max - x_min),
                "height": int(y_max - y_min),
                "confidence": float(confidence)
            }
            boxes.append(element)
        
        return {
            "extracted_text": extracted_text,
            "language": detected_language,
            "image_path": image_path,
            "text_boxes": boxes
        }
    except Exception as e:
        return {"error": str(e)}

def find_and_draw(image_path, target_text):
    """Finds specific text in the OCR result and draws a bounding box on the image."""
    try:
        ocr_result = extract_structured_data(image_path)
        image = preprocess_image(image_path)
        found_boxes = []
        
        for box in ocr_result.get("text_boxes", []):
            if target_text.lower() in box["text"].lower():
                x, y, w, h = box["x"], box["y"], box["width"], box["height"]
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                found_boxes.append(box)
        
        annotated_path = f"annotated_{image_path}"
        cv2.imwrite(annotated_path, image)
        
        return {
            "image_path": image_path,
            "annotated_image": annotated_path,
            "found_boxes": found_boxes
        }
    except Exception as e:
        return {"error": str(e)}
