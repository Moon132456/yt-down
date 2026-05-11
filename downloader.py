import yt_dlp
import os
import re
import json
import tempfile

# Temporary cookie file for better bot detection avoidance
COOKIE_CONTENT = """# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1745399424	CONSENT	YES+cb
"""

def get_video_info(url):
    # Create a temp cookie file
    cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    cookie_file.write(COOKIE_CONTENT)
    cookie_file.close()

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_file.name,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and 'entries' in info:
                info = info['entries'][0]
            
            if not info:
                raise Exception("No video info extracted")
            
            formats = []
            format_map = {}
            for f in info.get('formats', []):
                fid = f.get('format_id')
                if fid in format_map:
                    continue
                format_map[fid] = True
                
                if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                    format_data = {
                        'format_id': fid,
                        'ext': f.get('ext', 'mp4'),
                        'resolution': f'{f.get("height")}p' if f.get('height') else 'audio only',
                        'filesize': f.get('filesize', 0),
                        'acodec': f.get('acodec', 'none'),
                        'vcodec': f.get('vcodec', 'none'),
                        'type': 'video' if f.get('vcodec') != 'none' else 'audio',
                    }
                    formats.append(format_data)
            
            # Sort and return
            videos = [f for f in formats if f['type'] == 'video']
            audios = [f for f in formats if f['type'] == 'audio']
            videos.sort(key=lambda x: int(x['resolution'].replace('p', '')) if x['resolution'].isdigit() else 0, reverse=True)
            
            return {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'formats': videos + audios
            }
    except Exception as e:
        print(f"Error in get_video_info: {str(e)}")
        raise Exception(f"Could not extract video info. YouTube might have changed its API. Error: {str(e)[:100]}")
    finally:
        # Cleanup temp cookie file
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)

def download_media(url, format_id, output_path):
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
