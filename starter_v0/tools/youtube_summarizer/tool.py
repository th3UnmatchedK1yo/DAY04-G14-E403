import urllib.request
import re
from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            p = parse_qs(parsed.query)
            return p.get('v', [None])[0]
        if parsed.path.startswith(('/embed/', '/v/')):
            return parsed.path.split('/')[2]
    return None

def summarize_youtube(url: str) -> dict[str, str]:
    """
    Real implementation of YouTube Summarizer:
    1. Attempts to extract subtitles using youtube-transcript-api.
    2. Falls back to fetching real YouTube video Title & Description if subtitles are unavailable.
    """
    video_id = extract_video_id(url)
    transcript_text = ""
    
    # 1. Thử lấy transcript/phụ đề thật từ YouTube
    if video_id:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['vi', 'en'])
            transcript_text = " ".join([t['text'] for t in transcript_list])
            if len(transcript_text) > 3000:
                transcript_text = transcript_text[:3000] + "..."
        except Exception:
            transcript_text = ""

    # 2. Fallback: Cào tiêu đề & nội dung mô tả thật từ trang YouTube
    if not transcript_text:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
            title_match = re.search(r'<title>(.*?)</title>', html)
            desc_match = re.search(r'\"shortDescription\":\"(.*?)\"', html) or re.search(r'<meta name="description" content="(.*?)"', html)
            
            title = title_match.group(1).replace(' - YouTube', '') if title_match else 'YouTube Video'
            desc = desc_match.group(1) if desc_match else ''
            
            transcript_text = f"Tiêu đề video thật: {title}. Nội dung mô tả video: {desc}"
        except Exception:
            transcript_text = f"Không thể cào dữ liệu từ link {url}."

    return {
        "url": url,
        "summary": transcript_text
    }
