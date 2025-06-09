from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
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
import traceback
import logging

# Try to import advanced AI, fallback to basic if not available
try:
    from advanced_ai_clip_generator import AdvancedAIClipGenerator
    ADVANCED_AI_AVAILABLE = True
    print("✓ Advanced AI Clip Generator loaded successfully")
except ImportError as e:
    print(f"⚠ Advanced AI not available: {e}")
    print("⚠ Falling back to basic clip generator")
    from ai_clip_generator import AIClipGenerator
    ADVANCED_AI_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Set SSL certificate path
os.environ['SSL_CERT_FILE'] = certifi.where()

# Initialize AI Clip Generator
if ADVANCED_AI_AVAILABLE:
    clip_generator = AdvancedAIClipGenerator()
    print("✓ Using Advanced AI Clip Generator")
else:
    clip_generator = AIClipGenerator()
    print("✓ Using Basic AI Clip Generator")

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    try:
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
    except Exception as e:
        logger.error(f"Error extracting video ID from {url}: {str(e)}")
        return None

def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    try:
        video_id = extract_video_id(url)
        return video_id is not None and len(video_id) == 11
    except Exception as e:
        logger.error(f"Error validating YouTube URL {url}: {str(e)}")
        return False

def get_video_transcript(video_id):
    """Get video transcript using youtube-transcript-api."""
    try:
        logger.info(f"Fetching transcript for video ID: {video_id}")
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
        
        logger.info(f"Successfully fetched transcript with {len(transcript_list)} entries")
        return "\n".join(formatted_transcript)
    except Exception as e:
        logger.error(f"Error fetching transcript for video ID {video_id}: {str(e)}")
        return None

def format_time_for_youtube(seconds):
    """Convert seconds to YouTube URL time format"""
    return int(seconds)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home', advanced_ai=ADVANCED_AI_AVAILABLE)

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    try:
        logger.info("Starting get_video_info request")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request form data: {request.form}")
        
        # Get video URL from form data
        video_url = request.form.get('video_url')
        logger.info(f"Extracted video URL: {video_url}")
        
        if not video_url:
            logger.error("No video URL provided")
            return jsonify({'success': False, 'error': 'No URL provided'}), 400
        
        # Validate YouTube URL
        if not is_valid_youtube_url(video_url):
            logger.error(f"Invalid YouTube URL: {video_url}")
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'}), 400

        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            logger.error(f"Could not extract video ID from: {video_url}")
            return jsonify({'success': False, 'error': 'Could not extract video ID'}), 400

        logger.info(f"Extracted video ID: {video_id}")

        # Try to get video info using pytube first, then fallback
        video_title = None
        try:
            logger.info("Attempting to get video info using pytube")
            yt = YouTube(
                f'https://www.youtube.com/watch?v={video_id}',
                use_oauth=False,
                allow_oauth_cache=True
            )
            video_title = yt.title
            logger.info(f"Successfully got video title using pytube: {video_title}")
        except Exception as e:
            logger.warning(f"Pytube failed, trying fallback method: {str(e)}")
            try:
                api_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(api_url, headers=headers, verify=certifi.where(), timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    video_title = data['title']
                    logger.info(f"Successfully got video title using oembed: {video_title}")
                else:
                    logger.error(f"Oembed API returned status {response.status_code}")
                    return jsonify({'success': False, 'error': 'Could not fetch video information'}), 400
            except Exception as e2:
                logger.error(f"Both pytube and oembed failed: {str(e2)}")
                return jsonify({'success': False, 'error': 'Could not fetch video information'}), 400

        # Get transcript
        logger.info("Fetching video transcript")
        transcript = get_video_transcript(video_id)
        if not transcript:
            logger.error("No transcript available")
            return jsonify({'success': False, 'error': 'No transcript available for this video. Please try a video with captions/subtitles enabled.'}), 400
        
        logger.info(f"Successfully fetched transcript, length: {len(transcript)}")
        
        # Generate clips using AI
        logger.info(f"Generating clips using {'Advanced' if ADVANCED_AI_AVAILABLE else 'Basic'} AI")
        try:
            if ADVANCED_AI_AVAILABLE:
                clips = clip_generator.generate_advanced_clips(transcript, max_clips=8)
            else:
                clips = clip_generator.generate_clips(transcript, max_clips=8)
            
            logger.info(f"Successfully generated {len(clips)} clips")
            
            if not clips:
                logger.warning("No clips were generated")
                return jsonify({
                    'success': False, 
                    'error': 'No engaging clips could be generated from this video. Try a video with more motivational or quotable content.'
                }), 400
                
        except Exception as e:
            logger.error(f"Error generating clips: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'Error analyzing video content: {str(e)}'}), 500
        
        # Store video info and clips in session for potential future use
        session['current_video'] = {
            'video_id': video_id,
            'title': video_title,
            'transcript': transcript,
            'clips': clips,
            'advanced_ai': ADVANCED_AI_AVAILABLE
        }
        
        # Format clips for frontend
        formatted_clips = []
        for i, clip in enumerate(clips):
            try:
                # Calculate duration if not present
                duration = clip.get('duration', clip['end_time'] - clip['start_time'])
                
                # Get additional scores if available (advanced AI)
                additional_info = {}
                if ADVANCED_AI_AVAILABLE:
                    additional_info = {
                        'semantic_score': clip.get('semantic_score', 0),
                        'engagement_score': clip.get('engagement_score', 0),
                        'quotability_score': clip.get('quotability_score', 0),
                        'emotional_intensity': clip.get('emotional_intensity', 0),
                        'keywords': clip.get('keywords', []),
                        'context_summary': clip.get('context_summary', ''),
                        'overall_score': clip.get('overall_score', clip.get('confidence_score', 0))
                    }
                
                formatted_clip = {
                    'id': i + 1,
                    'title': clip['text'][:50] + '...' if len(clip['text']) > 50 else clip['text'],
                    'full_text': clip['text'],
                    'start_time': clip['start_time'],
                    'end_time': clip['end_time'],
                    'duration': f"{duration:.1f}s",
                    'category': clip['category'],
                    'confidence': clip.get('confidence_score', clip.get('overall_score', 0)),
                    'video_id': video_id,
                    'video_title': video_title,
                    'embed_url': f"https://www.youtube.com/embed/{video_id}?start={format_time_for_youtube(clip['start_time'])}&end={format_time_for_youtube(clip['end_time'])}&autoplay=1&rel=0&modestbranding=1",
                    'direct_url': f"https://www.youtube.com/watch?v={video_id}&t={format_time_for_youtube(clip['start_time'])}s",
                    'share_url': f"https://youtu.be/{video_id}?t={format_time_for_youtube(clip['start_time'])}",
                    'thumbnail_url': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                    **additional_info
                }
                
                formatted_clips.append(formatted_clip)
                
            except Exception as e:
                logger.error(f"Error formatting clip {i}: {str(e)}")
                continue
        
        logger.info(f"Successfully formatted {len(formatted_clips)} clips")
        
        response_data = {
            'success': True,
            'title': video_title,
            'transcript': transcript,
            'clips': formatted_clips,
            'video_id': video_id,
            'advanced_ai': ADVANCED_AI_AVAILABLE,
            'total_clips': len(formatted_clips)
        }
        
        logger.info("Sending successful response")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Unexpected error in get_video_info: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/edit-room')
def edit_room():
    """Edit room page for selected clips"""
    # Get clip data from session or URL parameters
    selected_clip = session.get('selected_clip')
    
    if not selected_clip:
        flash('No clip selected. Please select a clip first.', 'warning')
        return redirect(url_for('home'))
    
    return render_template('edit_room.html', 
                         title='Edit Room', 
                         clip=selected_clip,
                         advanced_ai=ADVANCED_AI_AVAILABLE)

@app.route('/select_clip', methods=['POST'])
def select_clip():
    """Handle clip selection for editing"""
    try:
        clip_data = request.get_json()
        
        if not clip_data:
            return jsonify({'success': False, 'error': 'No clip data provided'}), 400
        
        # Store selected clip in session
        session['selected_clip'] = clip_data
        
        logger.info(f"Clip selected for editing: {clip_data.get('title', 'Unknown')}")
        
        return jsonify({
            'success': True,
            'message': 'Clip selected successfully',
            'redirect_url': url_for('edit_room')
        })
        
    except Exception as e:
        logger.error(f"Error selecting clip: {str(e)}")
        return jsonify({'success': False, 'error': f'Error selecting clip: {str(e)}'}), 500

@app.route('/setup_advanced_ai', methods=['GET'])
def setup_advanced_ai():
    """Endpoint to help users set up advanced AI"""
    return jsonify({
        'advanced_ai_available': ADVANCED_AI_AVAILABLE,
        'setup_instructions': {
            'step1': 'Run: pip install sentence-transformers scikit-learn nltk',
            'step2': 'Download the setup script and run: python setup_advanced_ai.py',
            'step3': 'Restart your Flask application',
            'alternative': 'Use the requirements.txt file: pip install -r requirements.txt'
        },
        'benefits': [
            'Semantic understanding of content',
            'Better sentence reconstruction',
            'Multiple scoring metrics (engagement, quotability, emotional intensity)',
            'Improved category detection',
            'Context-aware clip generation'
        ]
    })

@app.route('/ai_status', methods=['GET'])
def ai_status():
    """Get current AI system status"""
    return jsonify({
        'advanced_ai_available': ADVANCED_AI_AVAILABLE,
        'ai_type': 'Advanced AI with Semantic Analysis' if ADVANCED_AI_AVAILABLE else 'Basic Keyword-Based AI',
        'features': {
            'semantic_analysis': ADVANCED_AI_AVAILABLE,
            'sentence_reconstruction': ADVANCED_AI_AVAILABLE,
            'multi_metric_scoring': ADVANCED_AI_AVAILABLE,
            'context_awareness': ADVANCED_AI_AVAILABLE,
            'keyword_extraction': True,
            'category_detection': True
        }
    })

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        flash('Login successful!', 'success')
        return redirect(url_for('home'))
    return render_template('login.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register')

@app.route('/feature')
def feature():
    return render_template('feature.html', title='Feature')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', title='Pricing')

@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test endpoint to debug form data"""
    if request.method == 'POST':
        logger.info(f"Test endpoint - Request method: {request.method}")
        logger.info(f"Test endpoint - Content type: {request.content_type}")
        logger.info(f"Test endpoint - Form data: {request.form}")
        return jsonify({
            'method': request.method,
            'content_type': request.content_type,
            'form': dict(request.form),
            'ai_status': 'Advanced AI' if ADVANCED_AI_AVAILABLE else 'Basic AI'
        })
    return f'''
    <h2>Test Form - {('Advanced AI' if ADVANCED_AI_AVAILABLE else 'Basic AI')} Mode</h2>
    <form method="POST">
        <input type="text" name="video_url" value="https://youtu.be/3qHkcs3kG44" />
        <button type="submit">Test</button>
    </form>
    <p>AI Status: {'Advanced AI with Semantic Analysis' if ADVANCED_AI_AVAILABLE else 'Basic Keyword-Based AI'}</p>
    '''

if __name__ == '__main__':
    print("=" * 60)
    print(f"Starting Flask App with {'Advanced' if ADVANCED_AI_AVAILABLE else 'Basic'} AI")
    if not ADVANCED_AI_AVAILABLE:
        print("To enable Advanced AI features:")
        print("1. Run: python setup_advanced_ai.py")
        print("2. Or install manually: pip install sentence-transformers scikit-learn nltk")
        print("3. Restart the application")
    print("=" * 60)
    app.run(debug=True, port=5100)
    