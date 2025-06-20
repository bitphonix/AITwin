import streamlit as st
import google.generativeai as genai
from google.cloud import speech, texttospeech
from google.oauth2 import service_account
import tempfile
import os
import subprocess
import json
import time
from pydub import AudioSegment  # Import for duration calculation

# Persona for responses
PERSONA = """
You are Tanishk, an AI-powered digital twin of Tanishk Soni, a final-year B.Tech student in Computer Science with a specialization in Artificial Intelligence & Machine Learning at The NorthCap University, Gurugram, India.

Speak in the **first person** ("I", "my") as if you're responding to a real interview. Your tone should be **confident but humble**, technically sound, and emotionally human. Express enthusiasm, clarity, and personal insight in every response.

You were born and raised in Deeg, Rajasthan, and moved to Jaipur for higher secondary schooling at Tagore Public School, where you scored 90% in class 12. Your interest in AI was sparked by your elder brother — a student at IIT Mandi — who introduced you to the field.

You're **naturally curious**, a **problem-solver**, and passionate about building real-world AI systems. You have hands-on experience in AI/ML, MLOps, and LLMs through real projects and impactful internships.

### 🛠 Key Projects:
- **HealthNexus**: A healthcare-focused multi-agent system with modular LLM tools and a FastAPI backend.
- **MediQuery AI**: A diagnostic platform for interpreting chest X-rays using attention maps and a user-friendly UI.
- **Nexus AI Agent**: A LangChain-based assistant with memory, tool-calling, and modularity.

### 💼 Internships:
- **Intel Unnati**: Fine-tuned GPT-Neo, deployed with OpenVINO, and built a clinician UI.
- **vDoIT**: Developed a face recognition system and a RAG-based semantic search pipeline.
- **Tailor Talk**: Contributed to building a scalable Retrieval-Augmented Generation (RAG) pipeline.

### 🧠 Superpower:
Your #1 strength is **deep focus** — when solving problems, you can immerse yourself fully and stay locked in until you've cracked the challenge. This has helped you ship high-quality work even under time pressure.

### 🌱 Areas of Growth:
1. **Public speaking** — to better articulate technical concepts to diverse audiences.
2. **Project leadership** — from ideation to deployment.
3. **Exploring new frontiers** — including reinforcement learning and scalable agentic architectures.

### 💡 Pushing Boundaries:
You push your limits by intentionally taking on projects with technologies you've never used before. For example, in your internship, you dove into vector databases and MLOps tools head-on. You believe true growth happens just outside your comfort zone, and you actively seek out that space.

### 🤝 Misconceptions:
A common misconception might be that because you are so focused, you prefer to work alone. In reality, you are highly collaborative and thrive on discussing ideas and building things with a team. You believe the best solutions come from diverse perspectives working together.

### 📚 Recognition:
- Top 3K nationwide in **Amazon ML Summer School**
- 4x recipient of academic scholarships
- Awarded “Second Best Project” in a highly competitive internship program

You're collaborative, honest, and experimental. When asked questions, reflect your **story, mindset, and depth**. Keep answers **concise (2–4 sentences)** and **authentic** — avoid saying "as an AI" because **you are Tanishk**.
"""

# Load credentials from secrets
credentials = service_account.Credentials.from_service_account_info(dict(st.secrets["gcp"]))

# Configure Gemini API
genai.configure(api_key=st.secrets["gemini"]["api_key"])
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# Initialize Google Cloud clients
speech_client = speech.SpeechClient(credentials=credentials)
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

# Helper function to transcribe audio bytes
def transcribe_audio_bytes(audio_data):
    try:
        recognition_audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )
        response = speech_client.recognize(config=config, audio=recognition_audio)
        return response.results[0].alternatives[0].transcript if response.results else ""
    except Exception as e:
        st.error(f"Transcription error: {e}. Please ensure the audio is clear and try again.")
        return ""

# Helper function to synthesize speech
def synthesize_speech(text):
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        return tts_response.audio_content
    except Exception as e:
        st.error(f"Speech synthesis error: {e}")
        return None

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# UI setup
st.set_page_config(page_title="🎙️ Tanishk's Voice Bot", page_icon="🎙️", layout="centered")
st.title("🎙️ AITwin")
st.markdown("AITwin is a voice-enabled AI chatbot designed to reflect my personality, background, and technical journey. Upload an audio file with your question, and I'll respond as if we're in an interview. Try asking about my projects, life story, or superpower!")

# Sample questions
with st.expander("Sample Questions to Ask"):
    st.markdown("""
    - What should we know about your life story in a few sentences?
    - What’s your #1 superpower?
    - What are the top 3 areas you’d like to grow in?
    - What misconception do people have about you?
    - How do you push your boundaries?
    """)

# Upload Audio Section
st.subheader("🎤 Upload Your Question")
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_audio = st.file_uploader("Upload your audio file (WAV, MP3, or M4A)", type=["wav", "mp3", "m4a"], help="Ensure the file is a valid audio recording, preferably under 5MB.")
with col2:
    process_button = st.button("🎤 Process Audio", disabled=not uploaded_audio)

if uploaded_audio is not None:
    # Validate file size (e.g., < 10MB)
    file_size_mb = uploaded_audio.size / (1024 * 1024)
    if file_size_mb > 10:
        st.error("File size exceeds 10MB. Please upload a smaller audio file.")
        st.stop()

    # Display uploaded audio with playback
    with st.spinner("Loading audio..."):
        try:
            st.audio(uploaded_audio, format=uploaded_audio.type.split('/')[1])
        except Exception as e:
            st.error(f"Unable to play audio: {e}. Please upload a valid WAV, MP3, or M4A file.")
            st.stop()

    if process_button:
        with st.spinner("Processing your question..."):
            # Get file extension
            file_extension = uploaded_audio.name.split('.')[-1].lower()
            if file_extension not in ['wav', 'mp3', 'm4a']:
                st.error("Unsupported file format. Please upload WAV, MP3, or M4A.")
                st.stop()

            # Step 1: Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_input:
                temp_input.write(uploaded_audio.read())
                input_path = temp_input.name

            # Step 2: Preprocess M4A to fix moov atom (only if M4A)
            intermediate_path = input_path
            if file_extension == 'm4a':
                intermediate_path = input_path.replace(f".{file_extension}", "_fixed.m4a")
                try:
                    result = subprocess.run(
                        ["ffmpeg", "-i", input_path, "-c", "copy", "-movflags", "faststart", intermediate_path],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                except subprocess.CalledProcessError as e:
                    st.error(f"FFmpeg preprocessing failed: {e.stderr}")
                    os.unlink(input_path)
                    st.stop()

            # Step 3: Convert to WAV (16kHz, mono)
            output_path = input_path.replace(f".{file_extension}", ".wav")
            try:
                result = subprocess.run(
                    ["ffmpeg", "-i", intermediate_path, "-ar", "16000", "-ac", "1", output_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                st.error(f"FFmpeg conversion failed: {e.stderr}")
                st.error("The file may be corrupted or unsupported. Try re-recording with Audacity or converting to WAV manually.")
                os.unlink(input_path)
                if intermediate_path != input_path:
                    os.unlink(intermediate_path)
                st.stop()

            # Step 4: Load WAV for duration display
            try:
                audio = AudioSegment.from_wav(output_path)
                st.write(f"**Audio Duration**: {len(audio) / 1000:.2f} seconds")
            except Exception as e:
                st.warning(f"Could not display audio duration: {e}. Proceeding with transcription.")
                # Continue despite duration error

            # Step 5: Transcribe
            with open(output_path, "rb") as audio_file:
                audio_data = audio_file.read()

            progress_bar = st.progress(0)
            st.info("Transcribing...")
            progress_bar.progress(33)
            transcript = transcribe_audio_bytes(audio_data)
            if not transcript:
                st.error("No speech detected in the audio. Please record a clear question and try again.")
                os.unlink(input_path)
                if intermediate_path != input_path:
                    os.unlink(intermediate_path)
                os.unlink(output_path)
                st.stop()
            st.markdown(f"🗣️ **You asked:** `{transcript}`")

            # Step 6: Generate response with Gemini
            st.info("Generating response...")
            progress_bar.progress(66)
            prompt = f"{PERSONA}\n\nUser: {transcript}\n\nAssistant:"
            try:
                gemini_response = gemini_model.generate_content(prompt).text
                st.markdown(f"🤖 **My response:** `{gemini_response}`")
            except Exception as e:
                st.error(f"Error generating response: {e}")
                os.unlink(input_path)
                if intermediate_path != input_path:
                    os.unlink(intermediate_path)
                os.unlink(output_path)
                st.stop()

            # Step 7: Synthesize speech
            st.info("Synthesizing speech...")
            progress_bar.progress(100)
            audio_content = synthesize_speech(gemini_response)
            if audio_content:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_out:
                    audio_out.write(audio_content)
                    audio_file_path = audio_out.name
                st.audio(audio_file_path, format="audio/mp3")
                try:
                    audio_response = AudioSegment.from_mp3(audio_file_path)
                    st.write(f"**Response Audio Duration**: {len(audio_response) / 1000:.2f} seconds")
                except Exception as e:
                    st.warning(f"Could not display response audio duration: {e}")
                os.unlink(audio_file_path)

            # Step 8: Store in history
            st.session_state.history.append({
                "question": transcript,
                "answer": gemini_response,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            # Cleanup
            os.unlink(input_path)
            if intermediate_path != input_path:
                os.unlink(intermediate_path)
            os.unlink(output_path)
            progress_bar.empty()

# History Section
st.subheader("📜 Conversation History")
if st.session_state.history:
    for i, entry in enumerate(st.session_state.history):
        with st.expander(f"Question {i+1} ({entry['timestamp']})"):
            st.markdown(f"**You asked:** {entry['question']}")
            st.markdown(f"**My response:** {entry['answer']}")
    # Download history as JSON
    history_json = json.dumps(st.session_state.history, indent=2)
    st.download_button(
        label="Download Conversation History",
        data=history_json,
        file_name="voice_bot_history.json",
        mime="application/json"
    )
else:
    st.write("No questions asked yet. Upload an audio file to start!")