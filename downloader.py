import yt_dlp
import os
import tempfile

def get_video_info(url):
    # Create a temporary cookies file (required for YouTube)
    cookie_content = """# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	0	CONSENT	YES+cb
.youtube.com	TRUE	/	TRUE	0	VISITOR_INFO1_LIVE	abc123
"""
    cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    cookie_file.write(cookie_content)
    cookie_file.close()
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_file.name,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash']
            }
        },
        'format': 'best',
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
                    resolution = f'{f.get("height")}p' if f.get('height') else 'audio only'
                    if not is_video:
                        resolution = 'audio only'
                    
                    formats.append({
                        'format_id': fid,
                        'ext': f.get('ext', 'mp4'),
                        'resolution': resolution,
                        'filesize': f.get('filesize', 0) or f.get('filesize_approx', 0),
                        'type': 'video' if is_video else 'audio'
                    })
            
            # Sort: highest resolution first
            def get_res_num(fmt):
                if fmt['resolution'] == 'audio only':
                    return 0
                try:
                    return int(fmt['resolution'].replace('p', ''))
                except:
                    return 0
            
            formats.sort(key=get_res_num, reverse=True)
            
            return {
                'title': info['title'],
                'thumbnail': info.get('thumbnail', ''),
                'formats': formats
            }
            
    except Exception as e:
        print(f"yt-dlp error: {str(e)}")
        raise Exception(f"Could not extract video info. Error: {str(e)[:100]}")
    finally:
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)

def download_media(url, format_id, output_path):
    cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    cookie_file.write("""# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	0	CONSENT	YES+cb
""")
    cookie_file.close()
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookie_file.name,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    finally:
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)
