from fastapi import FastAPI, HTTPException, Body
import subprocess
import time
import json
import easyocr


def adb_open_app(package_name):
    """Open an app using ADB."""
    command = f"adb shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
    subprocess.run(command, shell=True)

def adb_tap(x, y):
    """Perform a tap action at the given coordinates."""
    command = f"adb shell input tap {x} {y}"
    subprocess.run(command, shell=True)

def adb_swipe(x1, y1, x2, y2, duration=300):
    """Perform a swipe action from (x1, y1) to (x2, y2)."""
    command = f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}"
    subprocess.run(command, shell=True)

def adb_text_input(text):
    """Input text using ADB."""
    command = f"adb shell input text '{text}'"
    subprocess.run(command, shell=True)

def adb_key_event(keycode):
    """Send a key event (e.g., KEYCODE_HOME, KEYCODE_BACK)."""
    command = f"adb shell input keyevent {keycode}"
    subprocess.run(command, shell=True)

def execute_actions(actions):
    """Execute a list of actions with ADB commands."""
    for action in actions:
        action_type = action.get("type")
        if action_type == "tap":
            adb_tap(action["x"], action["y"])
        elif action_type == "swipe":
            adb_swipe(action["x1"], action["y1"], action["x2"], action["y2"], action.get("duration", 300))
        elif action_type == "text":
            adb_text_input(action["text"])
        elif action_type == "keyevent":
            adb_key_event(action["keycode"])
        time.sleep(action.get("delay", 0.5))  # Add a delay between actions

def process_ocr_results(ocr_results, target_texts=None):
    """Convert OCR-detected text positions into ADB actions based on target texts."""
    actions = []
    if target_texts is None:
        target_texts = []  # If no filters are provided, process all detected text
    
    for item in ocr_results.get("text_boxes", []):
        if "text" in item and item["text"].strip():
            if not target_texts or any(t.lower() in item["text"].lower() for t in target_texts):
                actions.append({"type": "tap", "x": item["x"] + item["width"] // 2, "y": item["y"] + item["height"] // 2})
    return actions
   
def adb_screenshot(output_path="screenshot.png"):
    """Takes a screenshot using ADB and saves it locally."""
    subprocess.run("adb shell screencap -p /sdcard/screenshot.png", shell=True)
    subprocess.run(f"adb pull /sdcard/screenshot.png {output_path}", shell=True)
    return output_path

def process_ocr(image_path, target_texts=None):
    """Extracts text and coordinates using OCR and returns matching elements."""
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image_path)
    
    detected_elements = []
    for res in results:
        text, confidence = res[1], res[2]
        (x_min, y_min), (x_max, y_max) = res[0][0], res[0][2]
        element = {"text": text, "x": int(x_min), "y": int(y_min), "width": int(x_max - x_min), "height": int(y_max - y_min), "confidence": confidence}
        
        if not target_texts or any(t.lower() in text.lower() for t in target_texts):
            detected_elements.append(element)
    
    return detected_elements 
   
if __name__ == "__main__":
     process_ocr("screenshot.png", "Shorts")