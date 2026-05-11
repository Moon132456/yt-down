import yt_dlp
import os
import re
import requests

def get_video_info(url):
    # Try with cookies first
    try:
        return get_video_info_with_cookies(url)
    except Exception as e:
        print(f"Cookie method failed: {str(e)}")
        # Fallback to no-cookies method
        try:
            return get_video_info_no_cookies(url)
        except Exception as e2:
            raise Exception(f"All methods failed: {str(e2)}")

def get_video_info_with_cookies(url):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'cookies.txt')
    
    if not os.path.exists(cookie_path):
        raise Exception("cookies.txt not found")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_path,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['web', 'android']}},
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info and 'entries' in info:
            info = info['entries'][0]
        
        if not info or 'title' not in info:
            raise Exception("No video info extracted")
        
        formats = []
        seen = set()
        for f in info.get('formats', []):
            fid = f.get('format_id')
            if fid in seen:
                continue
            seen.add(fid)
            
            is_video = f.get('vcodec') != 'none'
            is_audio = f.get('acodec') != 'none'
            
            if is_video or is_audio:
                resolution = 'audio only'
                if is_video and f.get('height'):
                    resolution = f"{f.get('height')}p"
                
                filesize = f.get('filesize') or f.get('filesize_approx') or 0
                formats.append({
                    'format_id': fid,
                    'ext': f.get('ext', 'mp4'),
                    'resolution': resolution,
                    'filesize': filesize,
                    'type': 'video' if is_video else 'audio'
                })
        
        # Remove duplicates
        unique = {}
        for f in formats:
            key = f['resolution'] if f['type'] == 'video' else 'audio'
            if key not in unique:
                unique[key] = f
        
        final = list(unique.values())
        final.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'] != 'audio only' else 0, reverse=True)
        
        return {
            'title': info['title'],
            'thumbnail': info.get('thumbnail', ''),
            'formats': final
        }

def get_video_info_no_cookies(url):
    """Fallback using public API (no cookies needed)"""
    # Extract video ID
    video_id = None
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]+)',
        r'(?:youtu\.be\/)([\w-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    
    if not video_id:
        raise Exception("Could not extract video ID")
    
    # Try Invidious API
    api_url = f"https://inv.riverside.rocks/api/v1/videos/{video_id}"
    response = requests.get(api_url, timeout=15)
    
    if response.status_code != 200:
        raise Exception("API request failed")
    
    data = response.json()
    formats = []
    
    for f in data.get('formatStreams', []):
        formats.append({
            'format_id': str(f.get('itag', '')),
            'ext': f.get('ext', 'mp4'),
            'resolution': f"{f.get('height', '720')}p",
            'filesize': f.get('size', 0),
            'type': 'video'
        })
    
    for f in data.get('adaptiveFormats', []):
        if f.get('type', '').startswith('audio'):
            formats.append({
                'format_id': str(f.get('itag', '')),
                'ext': f.get('ext', 'm4a'),
                'resolution': 'audio only',
                'filesize': f.get('size', 0),
                'type': 'audio'
            })
    
    return {
        'title': data.get('title', 'Unknown'),
        'thumbnail': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        'formats': formats
    }

def download_media(url, format_id, output_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'cookies.txt')
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    if os.path.exists(cookie_path):
        ydl_opts['cookiefile'] = cookie_path
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
