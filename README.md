# Detection Smarter

This repository contains a Flask-based API for image detection and text recognition using OpenCV and Tesseract. The API provides endpoints for uploading images, detecting objects or text within images, and downloading processed images.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [File Structure](#file-structure)
- [Migration to openai>=1.0.0](#migration-to-openai100)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/detection_smarter.git
    cd detection_smarter
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Start the Flask server:
    ```bash
    python src/api/index.py
    ```

2. The server will run on port `4721` by default. You can access the API at `http://localhost:4721`.

## API Endpoints

### Home

- **GET /**

    Returns a simple message to confirm the server is running.

    ```bash
    curl http://localhost:4721/
    ```

### Detect Image

- **POST /detect/image**

    Detect objects or text in an uploaded image.

    **Parameters:**
    - `image`: The image file to be uploaded.
    - `scene_option`: The scene option for detection.
    - `detect_option`: The detection option (`icon` or `text`).
    - `contrast` (optional): Contrast setting for text detection.
    - `option_compare` (optional): Option compare setting for text detection.
    - `threshold` (optional): Threshold setting for text detection.

    ```bash
    curl -F "image=@path/to/your/image.png" "http://localhost:4721/detect/image?scene_option=option&detect_option=icon"
    ```

### List Scene Images

- **GET /scene/list**

    List all scene images.

    ```bash
    curl http://localhost:4721/scene/list
    ```

### Download Image

- **GET /download/<image_name>**

    Download a processed image by name.

    ```bash
    curl http://localhost:4721/download/image_name.png
    ```

### Upload Scene Image

- **POST /scene/upload**

    Upload a new scene image.

    **Parameters:**
    - `image`: The image file to be uploaded.
    - `image_name`: The name to save the image as.

    ```bash
    curl -F "image=@path/to/your/image.png" "http://localhost:4721/scene/upload?image_name=image_name"
    ```

### Detect Text Tree

- **POST /detect/text/tree**

    Detect text in an uploaded image and return the text tree structure.

    **Parameters:**
    - `image`: The image file to be uploaded.
    - `contrast` (optional): Contrast setting for text detection.
    - `threshold` (optional): Threshold setting for text detection.

    ```bash
    curl -F "image=@path/to/your/image.png" "http://localhost:4721/detect/text/tree"
    ```

### Python Detect Image

- **POST /py/detect/image**

    Detect objects in an uploaded image using a Python-based detection method.

    **Parameters:**
    - `image`: The image file to be uploaded.
    - `nameTemplate`: The template name for detection.

    ```bash
    curl -F "image=@path/to/your/image.png" "http://localhost:4721/py/detect/image?nameTemplate=template_name"
    ```

## File Structure

```
detection_smarter/
├── src/
│   ├── api/
│   │   └── index.py          # Main Flask API server
│   ├── core/
│   │   ├── index.py          # Core detection logic
│   │   ├── scenes.py         # Scene image handling
│   │   └── tesseract.py      # Text detection logic
│   └── utils/
│       ├── result/           # Directory for processed images
│       └── image_scenes/     # Directory for scene images
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Migration to openai>=1.0.0

This project has been updated to use the new `openai` API interface. The `openai.Completion` method has been replaced with `openai.ChatCompletion.create`.

### Example Usage

```python
import openai

def get_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']
```

Make sure to update your `requirements.txt` to include `openai>=1.0.0`.

## Contributing

Feel free to submit issues or pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License.