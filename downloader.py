import yt_dlp
import os
import tempfile
import re

def get_video_info(url):
    # YouTube URL ko normalize karo (short link se full link nahi, lekin extractor ko sahi input do)
    # Agar URL 'youtu.be' hai toh yt-dlp khud handle kar leta hai, bas cookies aur proper args do
    
    # Temporary cookies file (YouTube ke liye jaroori)
    cookie_content = """# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	0	CONSENT	YES+cb
"""
    cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    cookie_file.write(cookie_content)
    cookie_file.close()
    
    # Force 'web' aur 'android' client use karo (bypass bot detection ke liye)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_file.name,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android'],  # Try web first then android
                'skip': ['hls', 'dash']               # Skip problematic formats
            }
        },
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # yt-dlp automatically handles both youtube.com/watch and youtu.be formats
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
                    
                    # Filesize handling
                    filesize = f.get('filesize') or f.get('filesize_approx') or 0
                    
                    formats.append({
                        'format_id': fid,
                        'ext': f.get('ext', 'mp4'),
                        'resolution': resolution,
                        'filesize': filesize,
                        'type': 'video' if is_video else 'audio'
                    })
            
            # Sort: highest resolution first
            formats.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'] != 'audio only' else 0, reverse=True)
            
            # Remove duplicate resolutions (keep best quality for each)
            unique_formats = {}
            for f in formats:
                key = f['resolution'] if f['type'] == 'video' else 'audio'
                if key not in unique_formats:
                    unique_formats[key] = f
            
            final_formats = list(unique_formats.values())
            
            return {
                'title': info['title'],
                'thumbnail': info.get('thumbnail', ''),
                'formats': final_formats
            }
            
    except Exception as e:
        print(f"yt-dlp error for URL {url}: {str(e)}")
        raise Exception(f"Could not extract video info. Error: {str(e)[:100]}")
    finally:
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)

def download_media(url, format_id, output_path):
    cookie_content = """# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	0	CONSENT	YES+cb
"""
    cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    cookie_file.write(cookie_content)
    cookie_file.close()
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_file.name,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'extractor_args': {'youtube': {'player_client': ['web', 'android']}}
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    finally:
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)
