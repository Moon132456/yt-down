import yt_dlp
import os
import tempfile

def get_video_info(url):
    # Create temp cookie file
    cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    cookie_file.write("""# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	0	CONSENT	YES+cb
""")
    cookie_file.close()
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookie_file.name,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'ignoreerrors': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and 'entries' in info:
                info = info['entries'][0]
            
            if not info:
                raise Exception("No video info extracted")
            
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f'{f.get("height")}p' if f.get('height') else 'audio only',
                        'filesize': f.get('filesize', 0),
                        'type': 'video' if f.get('vcodec') != 'none' else 'audio'
                    })
            
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'formats': formats
            }
    except Exception as e:
        raise Exception(f"yt-dlp error: {str(e)}")
    finally:
        os.unlink(cookie_file.name)

def download_media(url, format_id, output_path):
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
