import re

def is_valid_youtube_url(url):
    patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/',
        r'(https?://)?(www\.)?(m\.youtube\.com)/'
    ]
    return any(re.match(pattern, url) for pattern in patterns)
