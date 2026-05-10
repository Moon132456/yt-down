from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from downloader import get_video_info, download_media
from utils import is_valid_youtube_url
import os
import uuid

app = Flask(__name__)

# ✅ YEH CHANGE KARO - Allow all domains
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({
        "message": "YouTube Downloader API is running",
        "endpoints": {
            "POST /get_formats": "Get video formats (body: {'url': 'youtube_url'})",
            "POST /download": "Download video/audio (body: {'url': 'youtube_url', 'format_id': 'format_id'})"
        }
    })

@app.route('/get_formats', methods=['POST', 'OPTIONS'])
def get_formats():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    url = data.get('url')
    
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    try:
        info = get_video_info(url)
        return jsonify({
            "title": info['title'],
            "thumbnail": info['thumbnail'],
            "formats": info['formats']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    if request.method == 'OPTIONS':
        return '', 200
    
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
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
