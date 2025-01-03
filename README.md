# Group Photo Face Detector

A client-side web application that detects faces in group photos and allows you to perform reverse image searches on individual faces using Google Lens.

## Features

* Upload group photos through drag & drop or file selection
* Automatic face detection using face-api.js
* Crop individual faces with padding
* Direct Google Lens search integration for each detected face
* Fully client-side processing (no server required)
* Modern, responsive UI with TailwindCSS

## Technologies Used

* face-api.js for face detection
* TailwindCSS for styling
* Vanilla JavaScript
* HTML5 Canvas for image processing

## Usage

Simply open `index.html` in your web browser or host it on any static web hosting service like GitHub Pages.

### Using with GitHub Pages

1. Fork this repository
2. Go to your repository settings
3. Navigate to "Pages" under "Code and automation"
4. Under "Source", select "Deploy from a branch"
5. Select the branch you want to deploy (usually "main")
6. Click "Save"

Your site will be published at `https://[your-username].github.io/GroupPhotoList`

## How it Works

1. Upload a group photo through drag & drop or file selection
2. The application uses face-api.js to detect faces in the image
3. Each detected face is cropped with padding
4. Click on any detected face to search for similar faces using Google Lens

## Privacy

All processing is done entirely in your browser. No images are uploaded to any server (except when you choose to search with Google Lens).

## License

MIT License - see LICENSE file for details 