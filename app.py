from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from downloader import get_video_info, download_media
from utils import is_valid_youtube_url
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "YouTube Downloader API is running"})

@app.route('/get_formats', methods=['POST'])
def get_formats():
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

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format_id = data.get('format_id')
    
    if not url or not format_id:
        return jsonify({"error": "URL and format_id required"}), 400
    
    try:
        filename = f"{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        
        download_media(url, format_id, filepath)
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Cleanup after download
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
