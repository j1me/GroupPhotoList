from flask import Flask, request, send_file, jsonify, url_for
import os
import cv2
import uuid
import numpy as np

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/GroupPhoto'

# Create necessary directories
UPLOAD_FOLDER = 'static/uploads'
CROPPED_FOLDER = 'static/cropped'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CROPPED_FOLDER, exist_ok=True)

# Load OpenCV's DNN face detector
prototxt_path = "deploy.prototxt"
caffemodel_path = "res10_300x300_ssd_iter_140000.caffemodel"

# Download model files if they don't exist
if not os.path.exists(prototxt_path):
    prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
    os.system(f'curl -o {prototxt_path} {prototxt_url}')

if not os.path.exists(caffemodel_path):
    caffemodel_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
    os.system(f'curl -o {caffemodel_path} {caffemodel_url}')

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
            
            # Convert to x, y, w, h format
            x = x1
            y = y1
            w = x2 - x1
            h = y2 - y1
            
            faces.append({
                'bbox': (x, y, w, h),
                'confidence': float(confidence)
            })
    
    return faces

def get_url_with_root(path):
    """Helper function to generate URLs with the correct base path"""
    return f"/GroupPhoto{path}"

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Save the file
        filename = str(uuid.uuid4()) + '.jpg'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process image with OpenCV
        image = cv2.imread(filepath)
        if image is None:
            raise Exception("Failed to load image")

        # Store original dimensions
        height, width = image.shape[:2]
        
        # Resize if the image is too large
        max_dimension = 1200
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            image = cv2.resize(image, None, fx=scale, fy=scale)

        # Detect faces
        faces = detect_faces(image, confidence_threshold=0.6)  # Increased confidence threshold

        # Process detected faces
        cropped_faces = []
        for i, face in enumerate(faces):
            x, y, w, h = face['bbox']
            confidence = face['confidence']
            
            # Add padding around the face (proportional to face size)
            padding_percent = 0.15  # Reduced padding
            padding_x = int(w * padding_percent)
            padding_y = int(h * padding_percent)
            
            # Ensure coordinates are within image bounds
            x = max(x - padding_x, 0)
            y = max(y - padding_y, 0)
            w = min(w + 2*padding_x, image.shape[1] - x)
            h = min(h + 2*padding_y, image.shape[0] - y)
            
            # Crop face image
            face_image = image[y:y+h, x:x+w]
            
            # Save cropped face
            cropped_filename = f'face_{i}_{uuid.uuid4()}.jpg'
            cropped_filepath = os.path.join(CROPPED_FOLDER, cropped_filename)
            cv2.imwrite(cropped_filepath, face_image)
            
            cropped_faces.append({
                'id': i,
                'path': get_url_with_root(f'/static/cropped/{cropped_filename}'),
                'confidence': confidence
            })

        # Sort faces by confidence score
        cropped_faces.sort(key=lambda x: x['confidence'], reverse=True)

        return jsonify({
            'original_image': get_url_with_root(f'/static/uploads/{filename}'),
            'faces': cropped_faces,
            'total_faces': len(cropped_faces),
            'image_dimensions': f'{width}x{height}'
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_file(os.path.join('static', path))

if __name__ == '__main__':
    print("Starting server at http://localhost:5000/GroupPhoto")
    app.run(host='127.0.0.1', port=5000, debug=True) 