import cv2
import pytesseract

def preprocess_image(image_base64, threshold=177):
    image = cv2.imdecode(np.frombuffer(base64.b64decode(image_base64), np.uint8), cv2.IMREAD_GRAYSCALE)
    threshold_value = int(threshold)
    thresholded_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY_INV)[1]
    cv2.imwrite('src/utils/result/thresholded.png', thresholded_image)
    _, buffer = cv2.imencode('.png', thresholded_image)
    return base64.b64encode(buffer).decode('utf-8')

def detect_text(image_base64, detect_text='', option_compare='text', contrast=False, thresholds=[150,160,170,177,180,190,200]):
    best_confidence = 0
    best_threshold = 0
    best_coord = None
    saved_image_path = ''

    for threshold in thresholds:
        image_grey_scaled = preprocess_image(image_base64, threshold) if contrast else image_base64
        image = cv2.imdecode(np.frombuffer(base64.b64decode(image_grey_scaled), np.uint8), cv2.IMREAD_GRAYSCALE)
        
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        extracted_text = pytesseract.image_to_string(image)
        
        array = []
        if option_compare == 'line':
            array = [line for line in data['text'] if re.search(detect_text, line, re.IGNORECASE)]
        else:
            array = [word for word in data['text'] if re.search(detect_text, word, re.IGNORECASE)]
        
        if array:
            matched_element = array[0]
            coord = matched_element['bbox']
            confidence = matched_element['confidence']
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_threshold = threshold
                best_coord = coord

    if best_coord:
        y = (best_coord['top'] + best_coord['height']) / 2
        saved_image_path = draw_rectangle(best_coord, image_base64, 'src/utils/result')
        return {'x': (best_coord['left'] + best_coord['width']) / 2, 'y': y, 'threshold': best_threshold, 'confidence': best_confidence, 'saved_image_path': saved_image_path}
    
    return {'message': f'No {option_compare} found within threshold range.'}

def get_words_dom(image_base64, contrast=False, threshold=177):
    image_grey_scaled = preprocess_image(image_base64, threshold) if contrast else image_base64
    image = cv2.imdecode(np.frombuffer(base64.b64decode(image_grey_scaled), np.uint8), cv2.IMREAD_GRAYSCALE)
    
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    lines = data['text']
    
    if not lines:
        return {'message': 'Errors: No text found in the image'}
    
    for line in lines:
        del line['baseline'], line['page'], line['block'], line['paragraph']
        for word in line['words']:
            del word['baseline'], word['choices'], word['symbols'], word['font_id'], word['font_name'], word['font_size'], word['in_dictionary'], word['is_bold'], word['is_italic'], word['is_monospace'], word['is_serif'], word['is_smallcaps'], word['is_underlined']
    
    return lines
