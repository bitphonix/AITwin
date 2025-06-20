AITwin
AITwin is a voice-enabled AI chatbot designed to reflect the personality, background, and technical journey of Tanishk Soni, a final-year B.Tech student in Computer Science with a specialization in Artificial Intelligence & Machine Learning at The NorthCap University, Gurugram, India. Built with Streamlit, Google Cloud Speech-to-Text, Text-to-Speech, and Gemini AI, AITwin allows users to upload audio questions (WAV, MP3, or M4A) and receive spoken responses as if in an interview with Tanishk.
Features

Voice Interaction: Upload audio files to ask questions and receive spoken responses.
Personalized Responses: Answers reflect Tanishk’s life story, projects, and superpower (deep focus).
Conversation History: View and download a log of questions and answers in JSON format.
Robust Audio Processing: Supports WAV, MP3, and M4A files with FFmpeg preprocessing for reliable transcription.
Polished UI: Clean layout with progress bars, audio playback, and duration displays.

Sample Questions

What should we know about your life story in a few sentences?
What’s your #1 superpower?
What are the top 3 areas you’d like to grow in?
What misconception do people have about you?
How do you push your boundaries?

Prerequisites

Python 3.8+
FFmpeg (for audio processing)
Google Cloud account with Speech-to-Text and Text-to-Speech APIs enabled
Gemini AI API key

Installation

Clone the Repository:
git clone https://github.com/bitphonix/AITwin.git
cd AITwin


Set Up a Virtual Environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Install FFmpeg:

Windows: Download from FFmpeg’s site or choco install ffmpeg.
Mac: brew install ffmpeg.
Linux: sudo apt-get install ffmpeg.


Configure Secrets:Create a .streamlit/secrets.toml file with your API keys:
[gemini]
api_key = "your_gemini_api_key"

[gcp]
type = "service_account"
project_id = "your_gcp_project_id"
private_key_id = "your_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-client-email@your-project-id.iam.gserviceaccount.com"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-client-x509-cert-url"



Usage

Run Locally:streamlit run app.py


Open your browser to http://localhost:8501.
Upload an audio file (WAV, MP3, or M4A, <10MB).
Click "Process Audio" to hear AITwin’s response.
View and download conversation history in the "Conversation History" section.

Deployment to Streamlit Cloud

Push the repository to GitHub (ensure .gitignore excludes .streamlit/secrets.toml).
Create a Streamlit Cloud account and link your GitHub repo.
Add packages.txt with:ffmpeg


Add secrets in Streamlit Cloud’s settings (same as secrets.toml).
Deploy the app.

Project Structure
AITwin/
├── app.py               # Main Streamlit application
├── .streamlit/
│   ├── config.toml      # Streamlit theme configuration
├── requirements.txt     # Python dependencies
├── packages.txt         # System dependencies for Streamlit Cloud
├── .gitignore           # Excludes sensitive files
├── README.md            # Project documentation

Notes

Audio Files: For best results, use WAV files (16kHz, mono) to avoid format issues.
API Costs: Google Cloud APIs and Gemini may incur costs; check your quotas.
Contributing: Feel free to open issues or PRs to improve AITwin!

License
MIT License

Developed by Tanishk Soni. Connect with me on GitHub or LinkedIn!
