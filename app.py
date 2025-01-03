import os
from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np
from PIL import Image
import uuid
import sys

app = Flask(__name__)
app.debug = True

# Configure folders
UPLOAD_FOLDER = 'static/uploads'
CROPPED_FOLDER = 'static/cropped'
HTML_FOLDER = 'static'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CROPPED_FOLDER, exist_ok=True)
os.makedirs(HTML_FOLDER, exist_ok=True)

# Create index.html in static folder
index_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Group Photo Face Detection</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .drag-area { border: 2px dashed #4CAF50; transition: all 0.3s ease; }
        .drag-area.active { border-color: #2196F3; background-color: rgba(33, 150, 243, 0.1); }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-center mb-8">Group Photo Face Detection</h1>
        <div class="max-w-2xl mx-auto">
            <div class="drag-area bg-white p-8 rounded-lg shadow-md text-center mb-8">
                <div class="mb-4">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                    </svg>
                </div>
                <p class="text-gray-600 mb-4">Drag & Drop your group photo here or</p>
                <input type="file" id="file-input" class="hidden" accept="image/*">
                <button onclick="document.getElementById('file-input').click()" 
                        class="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded transition duration-300">
                    Choose File
                </button>
            </div>
            <div id="loading" class="hidden text-center mb-8">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p class="mt-4 text-gray-600">Processing image...</p>
            </div>
            <div id="results" class="hidden">
                <h2 class="text-2xl font-semibold mb-4">Original Photo</h2>
                <img id="original-image" class="w-full rounded-lg shadow-md mb-8" src="" alt="Original photo">
                <h2 class="text-2xl font-semibold mb-4">Detected Faces</h2>
                <div id="faces-grid" class="grid grid-cols-2 md:grid-cols-3 gap-4"></div>
            </div>
        </div>
    </div>
    <script>
        const dragArea = document.querySelector('.drag-area');
        const fileInput = document.getElementById('file-input');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const originalImage = document.getElementById('original-image');
        const facesGrid = document.getElementById('faces-grid');

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dragArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dragArea.addEventListener(eventName, () => dragArea.classList.add('active'));
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dragArea.addEventListener(eventName, () => dragArea.classList.remove('active'));
        });

        dragArea.addEventListener('drop', handleDrop, false);
        fileInput.addEventListener('change', handleFileSelect, false);

        function handleDrop(e) {
            handleFiles(e.dataTransfer.files);
        }

        function handleFileSelect(e) {
            handleFiles(e.target.files);
        }

        function handleFiles(files) {
            if (files.length === 0) return;
            
            const file = files[0];
            if (!file.type.startsWith('image/')) {
                alert('Please upload an image file');
                return;
            }

            loading.classList.remove('hidden');
            results.classList.add('hidden');

            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loading.classList.add('hidden');
                results.classList.remove('hidden');
                
                originalImage.src = data.original_image;
                
                facesGrid.innerHTML = '';
                data.faces.forEach(face => {
                    const faceElement = document.createElement('div');
                    faceElement.className = 'bg-white p-4 rounded-lg shadow-md';
                    faceElement.innerHTML = `
                        <img src="${face.path}" class="w-full h-48 object-cover rounded" alt="Face ${face.id + 1}">
                        <p class="mt-2 text-center text-gray-600">Person ${face.id + 1}</p>
                    `;
                    facesGrid.appendChild(faceElement);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                loading.classList.add('hidden');
                alert('An error occurred while processing the image');
            });
        }
    </script>
</body>
</html>
"""

with open(os.path.join(HTML_FOLDER, 'index.html'), 'w') as f:
    f.write(index_html)

# Load the pre-trained face detection cascade classifier
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

@app.route('/')
def index():
    return send_from_directory(HTML_FOLDER, 'index.html')

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
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
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

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Starting Flask application...")
    print(f"Server will be available at http://127.0.0.1:5000")
    print("Press Ctrl+C to quit")
    print("="*50 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=True) 