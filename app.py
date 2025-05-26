from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from datetime import datetime
from pytube import YouTube
import re
import ssl
import certifi
import os
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Set SSL certificate path
os.environ['SSL_CERT_FILE'] = certifi.where()

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        if parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        if parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[2]
    return None

def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    video_id = extract_video_id(url)
    return video_id is not None and len(video_id) == 11

def get_video_transcript(video_id):
    """Get video transcript using youtube-transcript-api."""
    try:
        # Get the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript with timestamps
        formatted_transcript = []
        for entry in transcript_list:
            text = entry['text']
            start = entry['start']
            minutes = int(start // 60)
            seconds = int(start % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            formatted_transcript.append(f"{timestamp} {text}")
        
        return "\n".join(formatted_transcript)
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")  # For debugging
        return None

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    try:
        video_url = request.form.get('video_url')
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        if not is_valid_youtube_url(video_url):
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Could not extract video ID'}), 400

        # Try to get video info using pytube
        try:
            yt = YouTube(
                f'https://www.youtube.com/watch?v={video_id}',
                use_oauth=False,
                allow_oauth_cache=True
            )
            video_title = yt.title
        except Exception as e:
            # Fallback to direct API request if pytube fails
            api_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(api_url, headers=headers, verify=certifi.where())
            if response.status_code == 200:
                data = response.json()
                video_title = data['title']
            else:
                return jsonify({'error': 'Could not fetch video information'}), 400

        # Get transcript
        transcript = get_video_transcript(video_id)
        
        return jsonify({
            'title': video_title,
            'transcript': transcript if transcript else 'No transcript available for this video.'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Add login logic here
        flash('Login successful!', 'success')
        return redirect(url_for('home'))
    return render_template('login.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Add registration logic here
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register')

if __name__ == '__main__':
    app.run(debug=True, port=5100)