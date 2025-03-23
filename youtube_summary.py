import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: No GEMINI_API_KEY found in .env file")
    exit()

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask
app = Flask(__name__)

# Setup CORS
cors_origin = os.getenv('CORS_ALLOW_ORIGIN', '*')
CORS(app, resources={r"/*": {"origins": cors_origin}}, supports_credentials=True)

# Setup rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute", "200 per hour"]
)

# Setup caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# List available models
@app.route('/list_models', methods=['GET'])
def list_models_route():
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        return jsonify({"models": model_names})
    except Exception as e:
        return jsonify({"error": f"Error listing models: {str(e)}"})

# Extract YouTube Video ID
def extract_video_id(video_url):
    if "youtube.com/watch?v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL format.")

# Fetch Transcript with detailed error logging
def get_video_transcript(video_id):
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to fetch transcript for video {video_id}, attempt {attempt+1}/{max_retries}")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = "\n".join([entry['text'] for entry in transcript])
            print(f"Successfully retrieved transcript for {video_id}, length: {len(transcript_text)} characters")
            return transcript_text
        except Exception as e:
            error_message = str(e)
            print(f"Error fetching transcript: {error_message}")
            
            # Detailed error analysis
            if "Too Many Requests" in error_message:
                print(f"YouTube rate limit detected: {error_message}")
                return f"Error fetching transcript (Rate limit): {error_message}"
            elif "Transcript unavailable" in error_message:
                print(f"No transcript available: {error_message}")
                return f"Error: This video does not have a transcript available. {error_message}"
            elif "not found" in error_message.lower():
                print(f"Video not found: {error_message}")
                return f"Error: Video ID {video_id} could not be found. {error_message}"
            
            # If not the final attempt, try again after delay
            if attempt < max_retries - 1:
                print(f"Retrying after {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"All {max_retries} attempts failed. Last error: {error_message}")
                return f"Error fetching transcript after {max_retries} attempts: {error_message}"

# Summarize Transcript with Gemini
def summarize_text(text):
    try:
        # Use the model that worked previously
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        response = model.generate_content(
            "Summarize the following YouTube video transcript into key points: \n\n" + text
        )
        return response.text
    except Exception as e:
        return f"Error generating summary: {e}"

# Answer questions with Gemini
def answer_question(transcript, question):
    try:
        # Use the model that worked previously
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        response = model.generate_content(
            f"Based on this YouTube video transcript: \n\n{transcript}\n\nAnswer this question: {question}"
        )
        return response.text
    except Exception as e:
        return f"Error answering question: {e}"

# Flask API Route to Get Summary
@app.route('/get_summary', methods=['GET'])
@limiter.limit("3 per minute")
@cache.cached(timeout=3600, query_string=True)  # Cache for 1 hour
def get_summary():
    video_url = request.args.get('video_url')  # Get YouTube link from request
    
    if not video_url:
        return jsonify({"error": "No video URL provided"})
    
    try:
        print(f"Processing request for video URL: {video_url}")
        video_id = extract_video_id(video_url)  # Extract video ID
        print(f"Extracted video ID: {video_id}")
        
        transcript = get_video_transcript(video_id)  # Fetch transcript

        if "Error" in transcript:
            print(f"Transcript error detected: {transcript}")
            if "Rate limit" in transcript:
                return jsonify({"error": f"YouTube rate limit reached. Please try again later. Details: {transcript}"})
            else:
                return jsonify({"error": transcript})

        print(f"Successfully retrieved transcript, generating summary...")
        summary = summarize_text(transcript)  # Generate summary
        print(f"Summary generated, length: {len(summary)} characters")
        return jsonify({"summary": summary})
    except Exception as e:
        print(f"Unexpected error in get_summary: {str(e)}")
        return jsonify({"error": f"Error processing request: {str(e)}"})

# New endpoint for asking questions
@app.route('/ask_question', methods=['POST'])
@limiter.limit("5 per minute")
def ask_question():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"})
    
    question = data.get('question')
    video_url = data.get('video_url')
    
    if not question:
        return jsonify({"error": "No question provided"})
    
    if not video_url:
        return jsonify({"error": "No video URL provided"})
    
    # Create a cache key based on video_url and question
    cache_key = f"{video_url}:{question}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return jsonify({"answer": cached_result})
    
    try:
        print(f"Processing question for video URL: {video_url}")
        video_id = extract_video_id(video_url)
        print(f"Extracted video ID: {video_id}")
        
        transcript = get_video_transcript(video_id)
        
        if "Error" in transcript:
            print(f"Transcript error detected: {transcript}")
            if "Rate limit" in transcript:
                return jsonify({"error": f"YouTube rate limit reached. Please try again later. Details: {transcript}"})
            else:
                return jsonify({"error": transcript})
        
        print(f"Successfully retrieved transcript, generating answer...")
        answer = answer_question(transcript, question)
        print(f"Answer generated, length: {len(answer)} characters")
        
        # Cache the result for 1 hour
        cache.set(cache_key, answer, timeout=3600)
        
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Unexpected error in ask_question: {str(e)}")
        return jsonify({"error": f"Error processing question: {str(e)}"})

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "api": "YouTube AI Chatbot API"})

# Run Flask App
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
