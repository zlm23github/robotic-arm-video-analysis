# Project

# Backend

## Minimum Requirements
- **Python**: >= 3.9 (3.10 recommended)
- **pip**: >= 20.x

## Environment
- python@3.10
- fastapi
- gemini

### Install required packages
```bash
python3.10 -m pip install --upgrade pip
pip install wheel
xcode-select --install # If not installed

pip install --only-binary=grpcio -r requirement.txt
```

### Check if all required packages are installed
```bash
pip list
```

### Configure .env
- GEMINI_API_KEY=YOUR_KEY

## Implemented Features (Backend)
- Support for uploading video files locally and downloading via URL
- Automatically saves uploaded videos to the `uploads` directory
- Provides an API to list all uploaded MP4 filenames
- Provides an API to analyze a specified video (using AI/model)
- Serves static files from the `/uploads` directory for direct video access
- CORS support for cross-origin requests

# FrontEnd

## Minimum Requirements
- **Node.js**: >= 16.x
- **npm**: >= 8.x
- **Browser**: Latest Chrome/Edge/Firefox recommended

## Environment
- Vite
- React
- Ant Design

### Install dependencies
```bash
npm install
```

### Run
```bash
npm run dev
```

## Implemented Features (Frontend)
- Upload video files (from local or via URL)
- Display all uploaded MP4 files in a dropdown list
- Preview the selected video directly in the browser
- Analyze the selected video by clicking a button
- Nicely formatted analysis results (by time range and action description)
- Analysis result area supports scrolling, and the page supports back-to-top



