
import streamlit as st
import base64
import json
import io
from gtts import gTTS
from pydub import AudioSegment
import groq

############################################
# 🔑 YOUR GROQ KEY (directly inserted)
############################################
GROQ_API_KEY = "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"

client = groq.Client(api_key=GROQ_API_KEY)

############################################
# 🎭 PROFILE MEMORY
############################################
PROFILE = {
    "life_story": "I grew up curious about computers and slowly turned that curiosity into building real things.",
    "superpower": "Learning very fast and explaining things simply.",
    "growth_areas": ["Public speaking", "Deep system design", "Team leadership"],
    "misconception": "People think I'm shy, but I'm actually observing and processing.",
    "boundaries": "I take monthly learning challenges to push myself out of comfort zones."
}

############################################
# 🔊 UTIL — Convert any audio → WAV 16k
############################################
def ensure_wav_bytes(file_bytes: bytes, filename: str):
    ext = filename.split(".")[-1].lower()
    audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=ext)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    buf = io.BytesIO()
    audio.export(buf, format="wav")
    return buf.getvalue()

############################################
# 🎙️ SPEECH TO TEXT — Groq Whisper
############################################
def speech_to_text(wav_bytes: bytes):
    resp = client.audio.transcriptions.create(
        file=("audio.wav", wav_bytes),
        model="whisper-large-v3"
    )
    return resp.text

############################################
# 🧠 LLM — Groq Chat API (LATEST, CORRECT)
############################################
def generate_reply(user_message, user_name):
    prompt = f"""
You are a personal AI agent for a job candidate.
Use these personality traits:

{PROFILE}

Always address the user by their name: {user_name}.
Speak naturally in 2–4 sentences.
Use the candidate's personality when answering.

User said: {user_message}
"""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful personal AI assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    reply = resp.choices[0].message.content   # FIXED
    return reply

############################################
# 🔊 TEXT TO SPEECH — gTTS
############################################
def tts(text):
    t = gTTS(text=text, lang="en")
    buf = io.BytesIO()
    t.write_to_fp(buf)
    return buf.getvalue()

############################################
# 🎨 UI START
############################################

st.set_page_config(page_title="Personal AI Voicebot", layout="centered")

st.title("🎤 Personal Voicebot (Groq + Mic Recorder)")
st.write("Single-file app. Fully updated and working.")

############################################
# LOGIN
############################################
st.sidebar.header("Login")
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""

username = st.sidebar.text_input("Your Name", value=st.session_state["user_name"])
if st.sidebar.button("Save Name"):
    st.session_state["user_name"] = username
    st.sidebar.success(f"Saved! Hello {username} 👋")

############################################
# MAIN MODES
############################################
mode = st.radio("Choose Mode", ["🎤 Mic Recording", "📤 Upload Audio", "⌨️ Text Input"])

############################################
# 🎤 MIC RECORDING
############################################
if mode == "🎤 Mic Recording":
    st.subheader("Record your voice")

    audio_data = st.audio_input("Click to record")

    if audio_data:
        wav_bytes = ensure_wav_bytes(audio_data.read(), "mic.wav")

        transcript = speech_to_text(wav_bytes)
        st.subheader("Transcript")
        st.write(transcript)

        reply = generate_reply(transcript, st.session_state["user_name"])
        st.subheader("Reply Text")
        st.write(reply)

        reply_audio = tts(reply)
        st.audio(reply_audio, format="audio/mp3")

############################################
# 📤 UPLOAD AUDIO
############################################
elif mode == "📤 Upload Audio":
    audio = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a", "ogg"])
    if audio:
        wav_bytes = ensure_wav_bytes(audio.read(), audio.name)

        transcript = speech_to_text(wav_bytes)
        st.subheader("Transcript")
        st.write(transcript)

        reply = generate_reply(transcript, st.session_state["user_name"])
        st.subheader("Reply Text")
        st.write(reply)

        reply_audio = tts(reply)
        st.audio(reply_audio, format="audio/mp3")

############################################
# ⌨️ TEXT MODE
############################################
else:
    text = st.text_area("Type your message…")
    if st.button("Send"):
        reply = generate_reply(text, st.session_state["user_name"])
        st.subheader("Reply Text")
        st.write(reply)

        reply_audio = tts(reply)
        st.audio(reply_audio, format="audio/mp3")

