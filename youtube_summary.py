import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv

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

# Enable CORS for all routes properly
cors_origin = os.getenv('CORS_ALLOW_ORIGIN', '*')
CORS(app, resources={r"/*": {"origins": cors_origin}}, supports_credentials=True)

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

# Fetch Transcript
def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return f"Error fetching transcript: {e}"

# Summarize Transcript with Gemini
def summarize_text(text):
    try:
        # Use text-generation model name format
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
        # Use text-generation model name format
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        response = model.generate_content(
            f"Based on this YouTube video transcript: \n\n{transcript}\n\nAnswer this question: {question}"
        )
        return response.text
    except Exception as e:
        return f"Error answering question: {e}"

# Flask API Route to Get Summary
@app.route('/get_summary', methods=['GET'])
def get_summary():
    video_url = request.args.get('video_url')  # Get YouTube link from request
    
    if not video_url:
        return jsonify({"error": "No video URL provided"})
    
    try:
        video_id = extract_video_id(video_url)  # Extract video ID
        transcript = get_video_transcript(video_id)  # Fetch transcript

        if "Error" in transcript:
            return jsonify({"error": transcript})

        summary = summarize_text(transcript)  # Generate summary
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"})

# New endpoint for asking questions
@app.route('/ask_question', methods=['POST'])
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
    
    try:
        video_id = extract_video_id(video_url)
        transcript = get_video_transcript(video_id)
        
        if "Error" in transcript:
            return jsonify({"error": transcript})
        
        answer = answer_question(transcript, question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": f"Error processing question: {str(e)}"})

# Run Flask App
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
