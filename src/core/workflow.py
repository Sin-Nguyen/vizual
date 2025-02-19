from fastapi import FastAPI, HTTPException, Body
import subprocess
import time
import json
from openai_chat_request import get_chat_completion
from core.adb_actions import adb_tap, adb_screenshot, process_ocr
import cv2
import re

def extract_steps(response_text):
    """Extract steps from the GPT response and return as a list."""
    steps = re.findall(r"\d+\.\s\*\*(.*?)\*\*", response_text)  # Extract bolded steps
    return steps if steps else response_text.split("\n")

def execute_workflow(query):
    """Executes the workflow dynamically by querying GPT for the next step after each action."""
    step = 0
    print(f"[Step {step+1}] Querying OpenAI for next action...")
    system_message = "As a QA engineer, you are an AI assistant for executing mobile app workflows."
    prompt = f"{query}. Given the previous step, what should be the next action?"
    response = get_chat_completion(prompt, system_message)
    
    # Extract the steps from the response
    steps = extract_steps(response)
    
    if step >= len(steps):
       print("No more steps found. Exiting workflow.")
       return
    for step in steps:
     # Perform the action based on the current step
     print(f"[Executing: {step}")
     step = step.lower()
     
     if "open" in step:
        adb_command = "adb shell monkey -p com.google.android.youtube 1"
          # Wait for the app to open

     elif "navigate" in step:
        adb_screenshot("screenshot.png")
        object = process_ocr("screenshot.png", "Shorts")
        x, y = object["text_boxes"][0]["x"], object["text_boxes"][0]["y"]
        print(f"Detected Shorts at: {x}, {y}")
        adb_command = f"adb shell input {x} {y}" 
        
     elif "browse" in step:
        adb_screenshot("screenshot.png")
        object = process_ocr("screenshot.png", "play")
        x, y = object["text_boxes"][0]["x"], object["text_boxes"][0]["y"]
        print(f"Detected Play button at: {x}, {y}")
        adb_command = f"adb shell input {x} {y}"
       
     else:
        adb_command = None  # If no matching action, skip
    
     if adb_command:
        print(f"Executing with adb: {adb_command}")
        subprocess.run(adb_command, shell=True)
        time.sleep(2)  # Add a delay between actions
        
if __name__ == "__main__":
    query = "I want to view short on youtube on android. How can I do that?"
    execute_workflow(query)