import yt_dlp
import requests
import json

def get_video_info(url):
    """
    Fetch video info using yt-dlp with proxy fallback.
    This bypasses YouTube's bot detection by using external APIs.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'extract_flat': False,
        'skip_download': True,
        # User-Agent spoofing to avoid detection
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Use a public proxy to bypass IP blocks (optional)
        # 'proxy': 'https://proxy-nl.secured.systems:8080', # Uncomment if needed
    }
    
    try:
        # Try direct extraction first
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info and 'entries' in info:
                info = info['entries'][0]
            
            if not info:
                raise Exception("No video info extracted")
            
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                    format_data = {
                        'format_id': f.get('format_id', ''),
                        'ext': f.get('ext', 'mp4'),
                        'resolution': f.get('height', 'audio only') if f.get('height') else 'audio only',
                        'filesize': f.get('filesize', 0),
                        'acodec': f.get('acodec', 'none'),
                        'vcodec': f.get('vcodec', 'none'),
                        'url': f.get('url', '')
                    }
                    
                    if format_data['vcodec'] != 'none':
                        format_data['type'] = 'video'
                    else:
                        format_data['type'] = 'audio'
                        format_data['resolution'] = 'audio only'
                    
                    if format_data['url']:  # Only add formats with valid URLs
                        formats.append(format_data)
            
            return {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'formats': formats
            }
            
    except Exception as e:
        # If yt-dlp fails, try alternative method via public API
        return get_video_info_via_api(url)


def get_video_info_via_api(url):
    """
    Fallback: Use a public YouTube info API (no authentication required)
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(url)
        if not video_id:
            raise Exception("Could not extract video ID")
        
        # Using invidious (public YouTube mirror) API - Free & No auth
        api_url = f"https://invidious.io.lol/api/v1/videos/{video_id}"
        
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            
            formats = []
            # Convert invidious formats to our format structure
            for f in data.get('formatStreams', []):
                formats.append({
                    'format_id': f.get('itag', ''),
                    'ext': f.get('ext', 'mp4'),
                    'resolution': f'{f.get("height", "audio")}p' if f.get('height') else 'audio only',
                    'filesize': f.get('size', 0),
                    'acodec': 'mp4a' if f.get('audioBitrate') else 'none',
                    'vcodec': 'avc1' if f.get('videoBitrate') else 'none',
                    'type': 'video' if f.get('videoBitrate') else 'audio',
                    'url': f.get('url', '')
                })
            
            # Add adaptive formats (audio only)
            for f in data.get('adaptiveFormats', []):
                if f.get('type', '').startswith('audio'):
                    formats.append({
                        'format_id': f.get('itag', ''),
                        'ext': f.get('ext', 'm4a'),
                        'resolution': 'audio only',
                        'filesize': f.get('size', 0),
                        'acodec': 'mp4a',
                        'vcodec': 'none',
                        'type': 'audio',
                        'url': f.get('url', '')
                    })
            
            return {
                'title': data.get('title', 'Unknown'),
                'thumbnail': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                'formats': formats
            }
        else:
            raise Exception("API request failed")
            
    except Exception as e:
        # Ultimate fallback: Return basic info only (audio/video both available)
        raise Exception(f"Could not extract video info: {str(e)}")


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    import re
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]+)',
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/v\/)([\w-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def download_media(url, format_id, output_path):
    """Download video/audio using yt-dlp with the selected format"""
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
