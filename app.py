import cv2
import numpy as np
import os
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CROPPED_FOLDER = 'cropped'

# Load the pre-trained face detection cascade classifier
prototxt_path = "deploy.prototxt"
caffemodel_path = "res10_300x300_ssd_iter_140000.caffemodel"

# Load the DNN model
face_net = cv2.dnn.readNet(prototxt_path, caffemodel_path)

def detect_faces(image, confidence_threshold=0.5):
    """
    Detect faces using OpenCV's DNN face detector.
    Returns list of faces with their bounding boxes and confidence scores.
    """
    height, width = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), [104, 117, 123], False, False)
    face_net.setInput(blob)
    detections = face_net.forward()
    
    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
            x1, y1, x2, y2 = box.astype(int)
            faces.append((x1, y1, x2 - x1, y2 - y1))
    
    return faces

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = str(uuid.uuid4()) + '.jpg'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        image = cv2.imread(filepath)
        if image is None:
            raise Exception("Failed to load image")
        
        # Detect faces using DNN
        faces = detect_faces(image, confidence_threshold=0.6)
        
        cropped_faces = []
        for i, (x, y, w, h) in enumerate(faces):
            padding = 30
            x = max(x - padding, 0)
            y = max(y - padding, 0)
            w = min(w + 2*padding, image.shape[1] - x)
            h = min(h + 2*padding, image.shape[0] - y)
            
            face_image = image[y:y+h, x:x+w]
            
            cropped_filename = f'face_{i}_{uuid.uuid4()}.jpg'
            cropped_filepath = os.path.join(CROPPED_FOLDER, cropped_filename)
            cv2.imwrite(cropped_filepath, face_image)
            
            cropped_faces.append({
                'id': i,
                'path': f'/static/cropped/{cropped_filename}'
            })
        
        return jsonify({
            'original_image': f'/static/uploads/{filename}',
            'faces': cropped_faces,
            'total_faces': len(cropped_faces)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500