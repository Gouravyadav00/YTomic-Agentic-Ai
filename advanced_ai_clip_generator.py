import re
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import requests
import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import logging

# Download required NLTK data with SSL fix
try:
    import ssl
    import certifi
    import os
    
    # Set SSL certificates
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            print(f"Warning: Could not download punkt tokenizer: {e}")
            print("Using fallback sentence tokenization")

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            print(f"Warning: Could not download stopwords: {e}")
            print("Using basic stopwords fallback")
            
except ImportError:
    print("Warning: SSL certificate setup failed, using fallback methods")

@dataclass
class AdvancedClip:
    start_time: int
    end_time: int
    text: str
    semantic_score: float
    engagement_score: float
    quotability_score: float
    emotional_intensity: float
    category: str
    keywords: List[str]
    context_summary: str

class AdvancedAIClipGenerator:
    def __init__(self, use_openai=False, openai_api_key=None):
        """
        Initialize the advanced AI clip generator
        
        Args:
            use_openai: Whether to use OpenAI API for enhanced analysis
            openai_api_key: OpenAI API key if using OpenAI
        """
        self.logger = logging.getLogger(__name__)
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key
        
        # Initialize sentence transformer for semantic similarity
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Loaded sentence transformer model")
        except Exception as e:
            self.logger.error(f"Failed to load sentence transformer: {e}")
            self.sentence_model = None
        
        # Enhanced motivational and quotable patterns
        self.viral_patterns = [
            # Success and achievement
            r'\b(success|achieve|accomplishment|victory|win|triumph)\b',
            # Failure and learning
            r'\b(fail|failure|mistake|learn|lesson|experience)\b',
            # Motivation and inspiration
            r'\b(inspire|motivate|encourage|empower|uplift)\b',
            # Wisdom and insight
            r'\b(wisdom|insight|truth|realize|understand|discover)\b',
            # Change and transformation
            r'\b(change|transform|evolve|grow|progress|improve)\b',
            # Leadership and influence
            r'\b(lead|leader|influence|impact|guide|mentor)\b',
            # Dreams and vision
            r'\b(dream|vision|goal|purpose|mission|aspire)\b',
            # Persistence and courage
            r'\b(persist|perseverance|courage|brave|determination|grit)\b',
            # Innovation and creativity
            r'\b(create|innovate|invent|original|unique|breakthrough)\b',
            # Life and happiness
            r'\b(life|happiness|joy|fulfillment|meaning|purpose)\b'
        ]
        
        # Engagement indicators
        self.engagement_patterns = [
            r'\b(amazing|incredible|unbelievable|shocking|surprising)\b',
            r'\b(secret|hidden|revealed|truth|reality)\b',
            r'\b(never|always|everyone|nobody|everything|nothing)\b',
            r'\b(most important|key|crucial|essential|fundamental)\b',
            r'\b(you need to|you have to|you must|you should)\b',
            r'\b(here\'s what|here\'s how|this is why|the reason)\b'
        ]
        
        # Emotional intensity indicators
        self.emotional_patterns = [
            r'\b(love|hate|fear|anger|joy|sadness|excitement)\b',
            r'\b(passionate|intense|powerful|strong|deep)\b',
            r'[!]{2,}|[?]{2,}',  # Multiple exclamation/question marks
            r'\b(wow|oh my god|incredible|unbelievable)\b'
        ]
        
        # Quotable sentence starters
        self.quotable_starters = [
            r'^(the|a) (key|secret|truth|reality|problem|solution) (is|to)',
            r'^(what|how|why|when|where) (you|we|people|most)',
            r'^(if you|when you|the moment you)',
            r'^(never|always|sometimes|often|rarely)',
            r'^(success|failure|life|happiness|love) (is|means|requires)',
            r'^(the difference between|what separates|what makes)',
            r'^(i learned|i realized|i discovered|i found)',
            r'^(here\'s|this is) (what|how|why|the)',
            r'^(you have to|you need to|you must|you should)',
            r'^(most people|everyone|nobody|few people)'
        ]
        
        # Initialize stopwords with fallback
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            # Fallback to basic stopwords if NLTK download failed
            self.stop_words = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 
                'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 
                'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 
                'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 
                'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
                'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 
                'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
                'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above', 
                'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 
                'further', 'then', 'once'
            }
            print("Using fallback stopwords due to NLTK download issues")
    
    def parse_transcript_advanced(self, transcript: str) -> List[Dict]:
        """Parse transcript with advanced text reconstruction"""
        lines = transcript.strip().split('\n')
        segments = []
        
        for line in lines:
            if not line.strip():
                continue
                
            # Extract timestamp
            timestamp_match = re.match(r'\[(\d{1,2}):(\d{2})\](.+)', line)
            if timestamp_match:
                minutes, seconds = map(int, timestamp_match.groups()[:2])
                start_seconds = minutes * 60 + seconds
                text = timestamp_match.group(3).strip()
                
                segments.append({
                    'start_time': start_seconds,
                    'text': text,
                    'original_line': line
                })
        
        return segments
    
    def reconstruct_sentences(self, segments: List[Dict], window_size: int = 10) -> List[Dict]:
        """Reconstruct complete sentences from fragmented segments"""
        reconstructed = []
        
        i = 0
        while i < len(segments):
            current_segment = segments[i]
            combined_text = current_segment['text']
            start_time = current_segment['start_time']
            end_time = current_segment['start_time'] + 3  # Default duration
            
            # Look ahead to combine fragments into complete sentences
            j = i + 1
            while j < min(i + window_size, len(segments)):
                next_segment = segments[j]
                
                # Check if we should combine with next segment
                if self._should_combine_segments(combined_text, next_segment['text']):
                    combined_text += " " + next_segment['text']
                    end_time = next_segment['start_time'] + 3
                    j += 1
                else:
                    break
            
            # Only add if the combined text meets minimum criteria
            if len(combined_text.split()) >= 5:  # At least 5 words
                reconstructed.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': combined_text.strip(),
                    'word_count': len(combined_text.split())
                })
            
            i = max(j, i + 1)  # Move forward
        
        return reconstructed
    
    def _should_combine_segments(self, current_text: str, next_text: str) -> bool:
        """Determine if two segments should be combined"""
        # Don't combine if current text ends with strong punctuation
        if current_text.strip().endswith(('.', '!', '?', ':')):
            return False
        
        # Don't combine if next text starts with capital letter (likely new sentence)
        if next_text and next_text[0].isupper():
            # Exception: if current text is very short, still combine
            if len(current_text.split()) < 3:
                return True
            return False
        
        # Don't combine if combined length would be too long
        combined_length = len((current_text + " " + next_text).split())
        if combined_length > 30:
            return False
        
        return True
    
    def calculate_semantic_score(self, text: str) -> float:
        """Calculate semantic relevance for motivational/quotable content"""
        if not self.sentence_model:
            return self._fallback_semantic_score(text)
        
        try:
            # Motivational reference sentences
            motivational_refs = [
                "Success comes from hard work and persistence",
                "Failure is the key to learning and growth",
                "You have the power to change your life",
                "Great achievements require courage and determination",
                "Innovation comes from thinking differently",
                "True happiness comes from within",
                "Leadership is about inspiring others",
                "Dreams become reality through action"
            ]
            
            # Get embeddings
            text_embedding = self.sentence_model.encode([text])
            ref_embeddings = self.sentence_model.encode(motivational_refs)
            
            # Calculate similarity scores
            similarities = cosine_similarity(text_embedding, ref_embeddings)[0]
            max_similarity = np.max(similarities)
            
            return float(max_similarity)
            
        except Exception as e:
            self.logger.error(f"Error in semantic scoring: {e}")
            return self._fallback_semantic_score(text)
    
    def _fallback_semantic_score(self, text: str) -> float:
        """Fallback semantic scoring without transformer model"""
        score = 0.0
        text_lower = text.lower()
        
        # Check for viral patterns
        for pattern in self.viral_patterns:
            if re.search(pattern, text_lower):
                score += 0.15
        
        # Check for quotable starters
        for pattern in self.quotable_starters:
            if re.search(pattern, text_lower):
                score += 0.2
                break
        
        return min(score, 1.0)
    
    def calculate_engagement_score(self, text: str) -> float:
        """Calculate engagement potential of the text"""
        score = 0.0
        text_lower = text.lower()
        
        # Check engagement patterns
        for pattern in self.engagement_patterns:
            matches = len(re.findall(pattern, text_lower))
            score += matches * 0.2
        
        # Check for numbers (specific claims are engaging)
        number_count = len(re.findall(r'\b\d+\b', text))
        score += min(number_count * 0.1, 0.3)
        
        # Check for questions
        question_count = text.count('?')
        score += min(question_count * 0.15, 0.3)
        
        # Check for imperatives (direct commands/advice)
        imperative_patterns = [r'\byou (need|should|must|have to|can|will)\b']
        for pattern in imperative_patterns:
            if re.search(pattern, text_lower):
                score += 0.2
        
        return min(score, 1.0)
    
    def calculate_quotability_score(self, text: str) -> float:
        """Calculate how quotable/shareable the text is"""
        score = 0.0
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Optimal length for quotes (10-25 words)
        if 10 <= word_count <= 25:
            score += 0.3
        elif 8 <= word_count <= 30:
            score += 0.2
        elif word_count < 8:
            score -= 0.2
        
        # Check for quotable starters
        for pattern in self.quotable_starters:
            if re.search(pattern, text_lower):
                score += 0.25
                break
        
        # Check for strong statements
        if any(word in text_lower for word in ['never', 'always', 'everyone', 'nobody', 'everything', 'nothing']):
            score += 0.2
        
        # Check for wisdom indicators
        wisdom_indicators = ['key', 'secret', 'truth', 'reality', 'important', 'remember']
        for indicator in wisdom_indicators:
            if indicator in text_lower:
                score += 0.1
        
        # Penalize questions (less quotable)
        if '?' in text:
            score -= 0.1
        
        return max(0.0, min(score, 1.0))
    
    def calculate_emotional_intensity(self, text: str) -> float:
        """Calculate emotional intensity of the text"""
        score = 0.0
        text_lower = text.lower()
        
        # Check emotional patterns
        for pattern in self.emotional_patterns:
            matches = len(re.findall(pattern, text_lower))
            score += matches * 0.2
        
        # Check for intensity markers
        intensity_markers = ['very', 'extremely', 'incredibly', 'absolutely', 'completely']
        for marker in intensity_markers:
            if marker in text_lower:
                score += 0.15
        
        # Check capitalization (indicates emphasis)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.1:  # More than 10% caps
            score += 0.2
        
        return min(score, 1.0)
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from the text"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stopwords and short words
        keywords = [word for word in words 
                   if word not in self.stop_words and len(word) > 3]
        
        # Count frequency and return top keywords
        from collections import Counter
        word_freq = Counter(keywords)
        return [word for word, _ in word_freq.most_common(5)]
    
    def categorize_content(self, text: str) -> str:
        """Categorize the content based on semantic analysis"""
        text_lower = text.lower()
        
        categories = {
            'Success & Achievement': ['success', 'achieve', 'accomplish', 'victory', 'win', 'goal'],
            'Personal Growth': ['grow', 'improve', 'develop', 'learn', 'change', 'transform'],
            'Leadership': ['lead', 'leader', 'manage', 'guide', 'influence', 'team'],
            'Motivation': ['motivate', 'inspire', 'encourage', 'empower', 'believe'],
            'Life Wisdom': ['life', 'wisdom', 'truth', 'understand', 'realize', 'meaning'],
            'Innovation': ['create', 'innovate', 'idea', 'think', 'original', 'unique'],
            'Relationships': ['people', 'relationship', 'love', 'family', 'friend', 'connect'],
            'Business': ['business', 'money', 'work', 'career', 'company', 'market'],
            'Mindset': ['mindset', 'attitude', 'think', 'believe', 'perspective', 'mind'],
            'Happiness': ['happy', 'joy', 'fulfillment', 'peace', 'content', 'satisfaction']
        }
        
        best_category = 'General'
        best_score = 0
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def generate_context_summary(self, text: str) -> str:
        """Generate a brief context summary"""
        # Simple extractive summary - take first and last parts if long
        words = text.split()
        if len(words) <= 15:
            return text
        
        # Take first 7 and last 7 words with ellipsis
        summary = ' '.join(words[:7]) + ' ... ' + ' '.join(words[-7:])
        return summary
    
    def generate_advanced_clips(self, transcript: str, max_clips: int = 8) -> List[Dict]:
        """Generate clips using advanced AI analysis"""
        try:
            # Parse and reconstruct sentences
            segments = self.parse_transcript_advanced(transcript)
            if not segments:
                return []
            
            reconstructed = self.reconstruct_sentences(segments)
            if not reconstructed:
                return []
            
            # Analyze each reconstructed segment
            analyzed_clips = []
            
            for segment in reconstructed:
                text = segment['text']
                
                # Skip very short or very long segments
                word_count = len(text.split())
                if word_count < 5 or word_count > 50:
                    continue
                
                # Calculate all scores
                semantic_score = self.calculate_semantic_score(text)
                engagement_score = self.calculate_engagement_score(text)
                quotability_score = self.calculate_quotability_score(text)
                emotional_intensity = self.calculate_emotional_intensity(text)
                
                # Calculate overall score (weighted combination)
                overall_score = (
                    semantic_score * 0.35 +
                    engagement_score * 0.25 +
                    quotability_score * 0.25 +
                    emotional_intensity * 0.15
                )
                
                # Only consider clips with decent scores
                if overall_score >= 0.3:
                    clip = AdvancedClip(
                        start_time=segment['start_time'],
                        end_time=segment['end_time'],
                        text=text,
                        semantic_score=semantic_score,
                        engagement_score=engagement_score,
                        quotability_score=quotability_score,
                        emotional_intensity=emotional_intensity,
                        category=self.categorize_content(text),
                        keywords=self.extract_keywords(text),
                        context_summary=self.generate_context_summary(text)
                    )
                    
                    analyzed_clips.append({
                        'start_time': clip.start_time,
                        'end_time': clip.end_time,
                        'text': clip.text,
                        'overall_score': overall_score,
                        'semantic_score': clip.semantic_score,
                        'engagement_score': clip.engagement_score,
                        'quotability_score': clip.quotability_score,
                        'emotional_intensity': clip.emotional_intensity,
                        'category': clip.category,
                        'keywords': clip.keywords,
                        'context_summary': clip.context_summary,
                        'duration': clip.end_time - clip.start_time,
                        'confidence_score': overall_score  # For backward compatibility
                    })
            
            # Sort by overall score and select diverse clips
            analyzed_clips.sort(key=lambda x: x['overall_score'], reverse=True)
            
            # Select diverse clips
            selected_clips = self._select_diverse_clips(analyzed_clips, max_clips)
            
            self.logger.info(f"Generated {len(selected_clips)} advanced clips from {len(analyzed_clips)} candidates")
            
            return selected_clips
            
        except Exception as e:
            self.logger.error(f"Error generating advanced clips: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _select_diverse_clips(self, clips: List[Dict], max_clips: int) -> List[Dict]:
        """Select diverse clips ensuring variety in categories and timing"""
        if len(clips) <= max_clips:
            return clips
        
        selected = []
        categories_used = set()
        
        # First pass: select best clips from different categories
        for clip in clips:
            if len(selected) >= max_clips:
                break
            
            category = clip['category']
            if category not in categories_used:
                selected.append(clip)
                categories_used.add(category)
        
        # Second pass: fill remaining slots with highest scoring clips
        remaining_clips = [c for c in clips if c not in selected]
        for clip in remaining_clips:
            if len(selected) >= max_clips:
                break
            
            # Ensure clips aren't too close to each other (at least 30 seconds apart)
            too_close = any(
                abs(clip['start_time'] - existing['start_time']) < 30
                for existing in selected
            )
            
            if not too_close:
                selected.append(clip)
        
        return selected[:max_clips]
    
    def refresh_advanced_clips(self, transcript: str, previous_clips: List[Dict], max_clips: int = 8) -> List[Dict]:
        """Generate new set of clips avoiding previously shown ones"""
        all_clips = self.generate_advanced_clips(transcript, max_clips * 2)
        
        # Filter out clips that are too similar to previous ones
        previous_start_times = {clip.get('start_time', 0) for clip in previous_clips}
        
        filtered_clips = []
        for clip in all_clips:
            # Check if this clip is too similar to any previous clip
            too_similar = any(
                abs(clip['start_time'] - prev_time) < 20 
                for prev_time in previous_start_times
            )
            
            if not too_similar:
                filtered_clips.append(clip)
        
        # If we don't have enough new clips, include some with lower threshold
        if len(filtered_clips) < max_clips:
            for clip in all_clips:
                if len(filtered_clips) >= max_clips:
                    break
                
                if clip not in filtered_clips:
                    too_similar = any(
                        abs(clip['start_time'] - prev_time) < 10
                        for prev_time in previous_start_times
                    )
                    
                    if not too_similar:
                        filtered_clips.append(clip)
        
        return filtered_clips[:max_clips]