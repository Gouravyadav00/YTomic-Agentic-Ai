from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

url="https://www.youtube.com/watch?v=pEiq3sI8dYQ&list=PLj0jSMWhCsdnsI6Pklh9Igru9dmUrHIxl"
parsed_url = urlparse(url)
if parsed_url.hostname in ['youtu.be']:
    print(parsed_url.path[1:])
if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
    if parsed_url.path == '/watch':
        url=parse_qs(parsed_url.query)['v'][0]
    if parsed_url.path[:7] == '/embed/':
        url= parsed_url.path.split('/')[2]
    if parsed_url.path[:3] == '/v/':
        url= parsed_url.path.split('/')[2]

print(url)
# Fetch transcript using the video ID
transcript = YouTubeTranscriptApi.get_transcript(url)

# Print the transcript (list of dicts)
for line in transcript:
    print(f"{line['start']:.2f}s: {line['text']}")
