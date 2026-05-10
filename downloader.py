import yt_dlp

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        formats = []
        for f in info['formats']:
            if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                format_data = {
                    'format_id': f['format_id'],
                    'ext': f['ext'],
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
                
                formats.append(format_data)
        
        return {
            'title': info['title'],
            'thumbnail': info['thumbnail'],
            'formats': formats
        }

def download_media(url, format_id, output_path):
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
