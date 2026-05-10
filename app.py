from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from downloader import get_video_info, download_media
from utils import is_valid_youtube_url
import os
import uuid

app = Flask(__name__)

# --- CORS Configuration (Global) ---
# Ye sabse important hai. Ye ensure karega ki sabhi routes ke liye
# CORS headers sahi se set ho.
CORS(app, 
     resources={r"/*": {
         "origins": ["https://yt5s.free.nf", "https://www.yt5s.free.nf", "*"],
         "methods": ["GET", "POST", "OPTIONS"], # IMPORTANT: OPTIONS ko explicitly add karo
         "allow_headers": ["Content-Type", "Authorization"]
     }},
     supports_credentials=True)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Home route (for GET request)
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "YouTube Downloader API is running",
        "endpoints": {
            "POST /get_formats": "Get video formats (body: {'url': 'youtube_url'})",
            "POST /download": "Download video/audio (body: {'url': 'youtube_url', 'format_id': 'format_id'})"
        }
    })

# --- get_formats route ---
# methods me 'OPTIONS' bhi add karna bohot zaroori hai.
@app.route('/get_formats', methods=['POST', 'OPTIONS'])
def get_formats():
    # Handle preflight request
    if request.method == 'OPTIONS':
        # Empty response with 200 OK
        response = make_response('', 200)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    # Handle actual POST request (Aapka original code)
    data = request.json
    url = data.get('url')
    
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    try:
        info = get_video_info(url)
        # Sending response with CORS headers
        response = jsonify({
            "title": info['title'],
            "thumbnail": info['thumbnail'],
            "formats": info['formats']
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- download route ---
@app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    # Handle actual POST request
    data = request.json
    url = data.get('url')
    format_id = data.get('format_id')
    
    if not url or not format_id:
        return jsonify({"error": "URL and format_id required"}), 400
    
    try:
        filename = f"{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        
        download_media(url, format_id, filepath)
        
        response = send_file(filepath, as_attachment=True)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

# Make sure make_response is imported
from flask import make_response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
