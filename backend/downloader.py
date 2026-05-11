import yt_dlp
import os

def get_video_info(url):
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'cookies.txt')
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_path,  # Use cookies file instead of browser
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info and 'entries' in info:
                info = info['entries'][0]
            
            if not info or 'title' not in info:
                raise Exception("No video info extracted")
            
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f'{f.get("height")}p' if f.get('height') else 'audio only',
                        'filesize': f.get('filesize', 0) or f.get('filesize_approx', 0),
                        'type': 'video' if f.get('vcodec') != 'none' else 'audio'
                    })
            
            return {
                'title': info['title'],
                'thumbnail': info.get('thumbnail'),
                'formats': formats
            }
    except Exception as e:
        raise Exception(f"yt-dlp error: {str(e)}")

def download_media(url, format_id, output_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'cookies.txt')
    
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
