import yt_dlp
import sys

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,  # important
        'extract_flat': False,
    }
    
    # Python 3.14+ ke liye patch
    if sys.version_info >= (3, 14):
        import urllib.request
        # monkey patch for yt-dlp compatibility
        if not hasattr(urllib.request, '_http_error'):
            urllib.request._http_error = lambda *args: None
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                raise Exception("Could not extract video info")
            
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                    format_data = {
                        'format_id': f.get('format_id', ''),
                        'ext': f.get('ext', ''),
                        'resolution': f.get('height', 'audio only'),
                        'filesize': f.get('filesize', 0),
                        'acodec': f.get('acodec', 'none'),
                        'vcodec': f.get('vcodec', 'none')
                    }
                    
                    if format_data['vcodec'] != 'none':
                        format_data['type'] = 'video'
                    else:
                        format_data['type'] = 'audio'
                        format_data['resolution'] = 'audio only'
                    
                    # remove duplicate entries
                    if not any(fmt['format_id'] == format_data['format_id'] for fmt in formats):
                        formats.append(format_data)
            
            return {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'formats': formats
            }
    except Exception as e:
        raise Exception(f"yt-dlp error: {str(e)}")

def download_media(url, format_id, output_path):
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
