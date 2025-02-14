import cv2
import numpy as np
import os
import sys

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"x:{self.x},y:{self.y}"

input_path = sys.argv[1]
template_path = sys.argv[2]

# Read the input screenshot and the template image
screenshot = cv2.imread(input_path)
template = cv2.imread(template_path, 0)

if screenshot is None:
    print(f"Error: Unable to read input image from {input_path}")

if template is None:
    print(f"Error: Unable to read template image from {template_path}")

# Convert the screenshot to grayscale
# gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
# Resize the screenshot to 25% of its original size
width = int(screenshot.shape[1] * 2)
height = int(screenshot.shape[0] * 2)
dim = (width, height)
screenshot = cv2.resize(screenshot, dim, interpolation=cv2.INTER_AREA)
gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

# Save the resized and grayscaled screenshot
cv2.imwrite('input_2.png', gray_screenshot)

# Perform template matching
result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)

# Set a threshold to detect the template
threshold = 0.8
loc = np.where(result >= threshold)

# Initialize coordinates as None
coordinates = None

# If we found at least one match, take the first one
if len(loc[0]) > 0:
    coordinates = (loc[1][0], loc[0][0])

# If no coordinates were found
# if coordinates is None:
#     print(f"Error: Not found selector '{os.path.splitext(os.path.basename(template_path))[0]}' in Base Image")
#     sys.exit()

cv2.rectangle(screenshot, coordinates, (coordinates[0] + template.shape[1], coordinates[1] + template.shape[0]), (0, 255, 0), 2)

# Save the result
output_dir = 'src/utils/result/'
os.makedirs(output_dir, exist_ok=True)
template_name = os.path.splitext(os.path.basename(template_path))[0]
output_name = f"{os.path.basename(input_path).split('.')[0]}_{template_name}_result.png"
output_path = os.path.join(output_dir, output_name)
cv2.imwrite(output_path, screenshot)

print(f"{Coordinate(int(coordinates[0]),int(coordinates[1]))}")