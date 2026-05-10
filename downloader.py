import yt_dlp
import sys

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        if info is None:
            raise Exception("Could not extract video info")
        
        formats = []
        seen_ids = set()
        
        for f in info.get('formats', []):
            format_id = f.get('format_id', '')
            if format_id in seen_ids:
                continue
            seen_ids.add(format_id)
            
            if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                format_data = {
                    'format_id': format_id,
                    'ext': f.get('ext', 'mp4'),
                    'resolution': f.get('height', 'audio only') if f.get('height') else 'audio only',
                    'filesize': f.get('filesize', 0),
                    'acodec': f.get('acodec', 'none'),
                    'vcodec': f.get('vcodec', 'none')
                }
                
                if format_data['vcodec'] != 'none':
                    format_data['type'] = 'video'
                else:
                    format_data['type'] = 'audio'
                    format_data['resolution'] = 'audio only'
                
                formats.append(format_data)
        
        return {
            'title': info.get('title', 'Unknown'),
            'thumbnail': info.get('thumbnail', ''),
            'formats': formats
        }

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
