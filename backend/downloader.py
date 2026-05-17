import yt_dlp
import os
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)

def get_video_info(url):
    """
    Extract video information and available formats from YouTube URL
    """
    # Absolute path to cookies
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'cookies.txt')
    
    # Check if cookies file exists
    if not os.path.exists(cookie_path):
        raise Exception(f"cookies.txt not found at {cookie_path}")
    
    print(f"✅ Using cookies from: {cookie_path}")
    
    # yt-dlp options for extracting video info
    ydl_opts = {
        'quiet': False,                    # Show errors (not quiet)
        'no_warnings': False,              # Show warnings
        'ignoreerrors': False,             # Don't ignore errors
        'cookiefile': cookie_path,         # Use cookies file
        'verbose': True,                   # Detailed output for debugging
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],  # Use android client (better rate limits)
                'skip': ['hls', 'dash'],              # Skip problematic formats
            }
        },
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        print(f"🔍 Fetching info for: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle playlist entries
            if info and 'entries' in info:
                info = info['entries'][0]
            
            # Validate info
            if not info or 'title' not in info:
                raise Exception("No video info extracted - video might be private or age-restricted")
            
            print(f"📹 Title: {info['title']}")
            
            # Extract available formats
            formats = []
            seen = set()
            
            for f in info.get('formats', []):
                fid = f.get('format_id')
                if fid in seen:
                    continue
                seen.add(fid)
                
                is_video = f.get('vcodec') != 'none'
                is_audio = f.get('acodec') != 'none'
                
                # Skip formats that are neither video nor audio
                if not is_video and not is_audio:
                    continue
                
                # Format resolution/quality label
                resolution = 'audio only'
                if is_video and f.get('height'):
                    resolution = f"{f.get('height')}p"
                elif is_video and f.get('resolution') and f.get('resolution') != 'none':
                    resolution = f.get('resolution')
                
                # Get file size
                filesize = f.get('filesize') or f.get('filesize_approx') or 0
                
                # Get bitrate if available
                bitrate = f.get('tbr') or f.get('vbr') or f.get('abr') or 0
                
                formats.append({
                    'format_id': fid,
                    'ext': f.get('ext', 'mp4'),
                    'resolution': resolution,
                    'filesize': filesize,
                    'filesize_mb': round(filesize / 1048576, 2) if filesize > 0 else 0,
                    'type': 'video' if is_video else 'audio',
                    'bitrate': round(bitrate, 0) if bitrate > 0 else 0,
                    'codec': f.get('vcodec') if is_video else f.get('acodec', 'unknown')
                })
            
            if not formats:
                raise Exception("No downloadable formats found for this video")
            
            # Remove duplicate resolutions (keep best quality for each)
            unique_formats = {}
            for f in formats:
                key = f['resolution'] if f['type'] == 'video' else 'audio'
                if key not in unique_formats:
                    unique_formats[key] = f
                else:
                    # Keep format with higher bitrate or better codec
                    existing = unique_formats[key]
                    if f['bitrate'] > existing['bitrate']:
                        unique_formats[key] = f
            
            final_formats = list(unique_formats.values())
            
            # Sort formats: highest video resolution first, then audio
            def sort_key(x):
                if x['type'] == 'video':
                    # Extract numeric resolution (e.g., "1080p" -> 1080)
                    res_num = 0
                    if 'p' in x['resolution']:
                        try:
                            res_num = int(x['resolution'].replace('p', ''))
                        except:
                            res_num = 0
                    return (1, -res_num)  # Higher resolution first
                else:
                    return (2, 0)  # Audio formats last
            
            final_formats.sort(key=sort_key)
            
            print(f"✅ Found {len(final_formats)} formats")
            
            # Return video info
            return {
                'title': info['title'],
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'formats': final_formats
            }
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            raise Exception("Cookie authentication failed. Please refresh your cookies file.")
        elif "Video unavailable" in error_msg:
            raise Exception("Video is unavailable (private, deleted, or age-restricted)")
        elif "copyright" in error_msg.lower():
            raise Exception("Video blocked due to copyright claim")
        else:
            raise Exception(f"YouTube extraction error: {error_msg}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise Exception(f"Failed to get video info: {str(e)}")


def download_media(url, format_id, output_path):
    """
    Download video/audio using specified format_id
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'cookies.txt')
    
    # Verify cookies exist
    if not os.path.exists(cookie_path):
        raise Exception(f"cookies.txt not found at {cookie_path}")
    
    print(f"📥 Downloading format: {format_id}")
    print(f"💾 Saving to: {output_path}")
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': False,
        'cookiefile': cookie_path,
        'verbose': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'progress_hooks': [progress_hook],  # Add progress callback
        'retries': 10,                      # Retry on failure
        'fragment_retries': 10,             # Retry fragments
        'skip_unavailable_fragments': True,
        'keep_fragments': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ Download completed: {output_path}")
        
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            raise Exception("Cookie authentication failed during download")
        elif "HTTP Error 403" in error_msg:
            raise Exception("Access forbidden - video might be age-restricted")
        else:
            raise Exception(f"Download failed: {error_msg}")
            
    except Exception as e:
        raise Exception(f"Download error: {str(e)}")


def progress_hook(d):
    """
    Callback function to show download progress
    """
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', '0 B/s').strip()
        eta = d.get('_eta_str', '0s').strip()
        print(f"\r📥 Downloading... {percent} at {speed} - ETA: {eta}", end='', flush=True)
        
    elif d['status'] == 'finished':
        print(f"\n✅ Download finished! Processing...")
        

def test_cookies():
    """
    Test function to verify cookies are working
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(script_dir, 'cookies.txt')
    
    if not os.path.exists(cookie_path):
        print("❌ cookies.txt file not found!")
        return False
    
    print(f"✅ Cookies file found at: {cookie_path}")
    
    # Try a simple extraction
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    ydl_opts = {
        'quiet': True,
        'cookiefile': cookie_path,
        'extractor_args': {'youtube': {'player_client': ['android']}},
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            print(f"✅ Cookies working! Video title: {info.get('title', 'Unknown')}")
            return True
    except Exception as e:
        print(f"❌ Cookies NOT working: {str(e)}")
        return False


# For local testing
if __name__ == '__main__':
    print("=== Testing YouTube Downloader ===")
    
    # Test cookies first
    test_cookies()
    
    # Test with a sample URL
    test_url = input("\nEnter YouTube URL to test (or press Enter to skip): ").strip()
    if test_url:
        try:
            info = get_video_info(test_url)
            print(f"\n✅ Video: {info['title']}")
            print(f"📊 Found {len(info['formats'])} formats:")
            for f in info['formats']:
                size_mb = f.get('filesize_mb', 0)
                print(f"   - {f['type']}: {f['resolution']} ({f['ext']}) - {size_mb} MB")
        except Exception as e:
            print(f"❌ Error: {e}")
