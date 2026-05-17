from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from downloader import get_video_info, download_media
from utils import is_valid_youtube_url
import os
import uuid
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# ✅ FIXED CORS Configuration
CORS(app, 
     resources={r"/*": {
         "origins": [
             "https://yt5s.free.nf",
             "http://yt5s.free.nf",
             "https://*.free.nf",
             "http://localhost:3000",
             "http://localhost:5500",
             "http://127.0.0.1:5500"
         ],
         "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
         "allow_headers": ["Content-Type", "Authorization", "Accept"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": True,
         "max_age": 3600
     }})

# Alternative: Allow all origins for testing (uncomment if above doesn't work)
# CORS(app, resources={r"/*": {"origins": "*"}})

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    return jsonify({
        "message": "YouTube Downloader API is running",
        "status": "active",
        "cors_enabled": True
    })

@app.route('/get_formats', methods=['POST', 'OPTIONS'])
def get_formats():
    """Get available formats for a YouTube video"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        if not is_valid_youtube_url(url):
            return jsonify({"error": "Invalid YouTube URL"}), 400
        
        print(f"📺 Fetching formats for: {url}")
        
        info = get_video_info(url)
        
        response = jsonify(info)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"❌ Error in get_formats: {str(e)}")
        error_response = jsonify({"error": str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

@app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    """Download video/audio file"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    url = data.get('url')
    format_id = data.get('format_id')
    
    if not url or not format_id:
        return jsonify({"error": "URL and format_id required"}), 400
    
    filepath = None
    
    try:
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        
        print(f"📥 Downloading: {url} (format: {format_id})")
        
        download_media(url, format_id, filepath)
        
        # Check if file exists
        if not os.path.exists(filepath):
            raise Exception("Download failed - file not created")
        
        # Send file
        response = send_file(
            filepath,
            as_attachment=True,
            download_name=f"video_{uuid.uuid4().hex[:8]}.mp4",
            mimetype='video/mp4'
        )
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        
        return response
        
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        error_response = jsonify({"error": str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500
        
    finally:
        # Clean up temp file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"🗑️ Deleted temp file: {filepath}")
            except Exception as e:
                print(f"⚠️ Could not delete temp file: {e}")

def _build_cors_preflight_response():
    """Build CORS preflight response"""
    response = jsonify({'message': 'CORS preflight successful'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.errorhandler(404)
def not_found(error):
    response = jsonify({"error": "Endpoint not found"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 404

@app.errorhandler(500)
def internal_error(error):
    response = jsonify({"error": "Internal server error"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
