import re

def is_valid_youtube_url(url):
    patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/',
        r'(https?://)?(www\.)?(m\.youtube\.com)/'
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False
