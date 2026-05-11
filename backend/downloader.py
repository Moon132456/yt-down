import yt_dlp
import os

# Get absolute path to cookies.txt
def get_cookie_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'cookies.txt')

def get_video_info(url):
    cookie_path = get_cookie_path()
    
    if not os.path.exists(cookie_path):
        raise Exception(f"cookies.txt not found at {cookie_path}")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_path,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android'],
            }
        },
    }
    
    try:
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
            
    except Exception as e:
        raise Exception(f"yt-dlp error: {str(e)}")

def download_media(url, format_id, output_path):
    cookie_path = get_cookie_path()
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_path,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
