# 🎥 YouTube AI Summarizer

This tool uses AI to grab YouTube video transcripts and whip up quick summaries. You can also ask it questions about the video content, thanks to some powerful language models (LLMs) under the hood.

## 🚀 What it Can Do
- Pulls transcripts straight from public YouTube videos.
- Creates both detailed and to-the-point summaries via OpenAI or Gemini.
- Got questions about the video? Get answers in a snap.
- Easy-to-use from your command line, with browser extension support on the way.
- Built for speed and real-time use right within YouTube.

## 🛠 Tech Stack
- **Language**: Python 3.10+
- **APIs**:
  - YouTube Transcript API
  - OpenAI GPT-4 / Gemini Pro (via Google Generative Language API)
- **Libraries**:
  - `youtube-transcript-api`
  - `openai`, `google.generativeai`
  - `requests`, `dotenv`
- **Frontend (Optional)**:
  - ReactJS + Chrome Extension (coming soon!)

## 📁 How It's Organized
Here's a look at how the project is laid out:
youtube_ai_summarizer/
│
├── youtube_summary.py          # Main script for fetching + summarizing
├── summarizer.py               # Does the LLM-based summarization
├── qa_agent.py                 # Handles Q&amp;A with the transcript (optional)
├── utils.py                    # Helper functions
├── .env                        # Your API keys live here (keep it secret!)
├── requirements.txt            # What Python packages you'll need
└── README.md                   # You're looking at it!


## 🔑 Getting Started
Setting this up is pretty straightforward. Just follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/youtube-ai-summarizer.git](https://github.com/yourusername/youtube-ai-summarizer.git)
cd youtube-ai-summarizer

2. Create a Virtual Environment (Recommended)
Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Set Up Your API Keys
Create a .env file in the main project folder and pop your API keys in there:

Ini, TOML

OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
🧠 How to Use It
To Summarize a YouTube Video
Ready to summarize? Here’s how:

Bash

python youtube_summary.py --url "[https://www.youtube.com/watch?v=VIDEO_ID](https://www.youtube.com/watch?v=VIDEO_ID)"
This will:

Grab the video's transcript.
Clean it up.
Send it off to your chosen LLM.
Give you back a neat summary.
Want to ask questions?
You can also quiz the video content:

Bash

python youtube_summary.py --url "..." --question "What are the key points?"
🧪 Example Output
Here’s a sneak peek of what you can expect:

YAML

📽 Title: "The Future of AI by Sam Altman"
📝 Summary: This video dives into the future of AI, covering ethical points, AGI timelines, and economic effects. Sam really pushes for open collaboration and touches on how important regulation and innovation are.
❓ Q: What risks does Sam Altman mention?
💡 A: He talks about the challenge of AI alignment, the risk of bad actors misusing AI, and governments being slow with new policies.
📦 What's Next?
We've got more cool stuff planned:

✅ Slick Chrome Extension for YouTube
✅ See summaries in real-time, right on YouTube
⏳ Option to save/export summaries (PDF/Markdown)
⏳ Automatic language detection and translation for summaries
⏳ Personal accounts and a dashboard for your summaries
🧠 Credits
This project was put together by Meharbir Chawla, with a little help from OpenAI & Google's LLMs.

📜 License
MIT License. Feel free to use it, fork it, and contribute!


**A few notes on the changes:**
* I've used slightly more conversational phrases (e.g., "whip up quick summaries," "Get answers in a snap," "pop your API keys in there").
* Some bullet points are rephrased to be more active or benefit-driven.
* Introductions to sections are a bit warmer.
* The final "You're all set!" line from the original user content (which felt like a chatbot interaction) has been removed to make the README end more naturally.

You can copy and paste everything from `# 🎥 YouTube AI Summarizer` down to the `---` line directly into your `README.md` file. Let me know if this feels closer to what you were looking for!



