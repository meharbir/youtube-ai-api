from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import openai

# OpenAI API Key
import os

OPENAI_API_KEY = "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"  # Replace with your actual OpenAI API key

# Configure OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize Flask (removed duplicate initialization)
app = Flask(__name__)

# Enable CORS for all routes properly
CORS(app, supports_credentials=True, origins="*")

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

# Summarize Transcript with GPT-4
def summarize_text(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following YouTube video transcript into key points."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {e}"

# Answer questions about the video
def answer_question(transcript, question):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that answers questions about YouTube videos based on their transcript."},
                {"role": "user", "content": f"Transcript: {transcript}\n\nQuestion: {question}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
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
    app.run(host="0.0.0.0", port=5000, debug=True)