# Group Photo Face Detector

A web-based tool that detects faces in group photos and allows you to perform reverse image searches on individual faces using Google Lens.

## Features

- Upload group photos
- Automatic face detection using face-api.js
- Crop individual faces with padding
- Direct Google Lens search integration for each detected face
- Fully client-side processing (no server required)
- Modern, responsive UI

## Live Demo

Visit [https://jimmeyjose.com/GroupPhoto](https://jimmeyjose.com/GroupPhoto)

## Local Development

1. Clone this repository
2. Open `index.html` in your web browser
3. Start uploading photos!

## Deployment on GitHub Pages

1. Fork this repository
2. Go to your repository settings
3. Navigate to "Pages" under "Code and automation"
4. Under "Source", select "Deploy from a branch"
5. Select the branch you want to deploy (usually "main" or "master")
6. Select the root folder (/) as the source
7. Click "Save"

Your site will be published at `https://[your-username].github.io/[repository-name]`

## Technologies Used

- face-api.js for face detection
- TailwindCSS for styling
- Vanilla JavaScript
- HTML5 Canvas for image processing

## License

MIT License - see LICENSE file for details 