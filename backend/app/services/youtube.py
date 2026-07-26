import re
from typing import Optional

def extract_youtube_video_id(url: Optional[str]) -> Optional[str]:
    """
    Extract YouTube video ID from various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    if not url:
        return None
    
    # Trim URL
    url = url.strip()
    
    # Regex patterns
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?\/]|$)',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'youtube\.com\/embed\/([0-9A-Za-z_-]{11})',
        r'youtube\.com\/watch\?v=([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    return None

def get_youtube_thumbnail(video_id: Optional[str]) -> Optional[str]:
    """
    Generate YouTube high quality thumbnail URL from video ID.
    """
    if not video_id:
        return None
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
