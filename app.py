import io
import asyncio
import base64
import streamlit as st
from groq import Groq
from audio_recorder_streamlit import audio_recorder
import edge_tts
from gtts import gTTS

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Praveen AI", page_icon="🎤", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    .block-container {padding-top: 0rem !important; padding-bottom: 0rem !important; max-width: 1200px !important; margin: 0 auto !important;}
    header {visibility: hidden;}
    .stApp {background: linear-gradient(180deg, #06152d 0%, #000a16 100%); padding: 0 !important; margin: 0 !important;}

    .header {padding: 50px; border-bottom: 1px solid rgba(0,145,255,0.4); background: rgba(0, 30, 70, 0.3); text-align: center; margin-top: 200px;}
    .title {color: #4DC0FF; font-size: 32px; font-weight: 700; margin: 0;}
    .sub {color: #9ED7FF; font-size: 18px; margin: 10px 0 0;}
    .status {padding: 25px 40px; color: #8CD2FF; font-size: 18px; background: rgba(0, 80, 160, 0.1);}
    .body {min-height: 150px; max-height: 250px; padding: 35px 40px; overflow-y: auto; display: flex; flex-direction: column;}
    .empty {display: none;}
    .stAudioRecorder {margin-top: 20px; background: transparent !important;}
    .stAudioRecorder > div {background: transparent !important; border: none !important; box-shadow: none !important;}
    [data-testid="stVerticalBlock"] > div:has(.stAudioRecorder) {background: transparent !important;}
    .element-container:has(.stAudioRecorder) {background: transparent !important;}
    .msg {max-width: 72%; padding: 11px 16px; margin: 8px 0; border-radius: 16px; font-size: 14.5px; line-height: 1.5;}
    .user {align-self: flex-end; background: #0f2a4f; color: #e1f0ff; border: 1px solid rgba(0,120,255,0.3);}
    .bot {align-self: flex-start; background: #061c33; color: #bfe3ff; border: 1px solid rgba(0,100,200,0.3);}
    .footer {padding: 40px 40px; border-top: 1px solid rgba(0,145,255,0.4); background: rgba(0, 30, 70, 0.2);}
    .control-card {background: linear-gradient(135deg, #4a90e2, #5ba3f5) !important; border-radius: 20px !important; padding: 25px !important; box-shadow: 0 4px 15px rgba(0,100,200,0.3) !important;}
    .input-fake {width: 100%; padding: 12px 20px; border-radius: 999px; border: 1px solid rgba(0,145,255,0.5); background: rgba(8,30,60,0.7); color: #9ED7FF; font-size: 14px; text-align: center; margin-bottom: 12px;}
    .stButton > button {width: 100px !important; height: 50px !important; border-radius: 25px !important; background: linear-gradient(135deg, #073567, #042544) !important; border: 1.5px solid #0a84ff !important; color: #9ED7FF !important; font-size: 14px !important; font-weight: 600 !important; box-shadow: 0 0 15px rgba(0,132,255,0.5);}
    [data-testid="column"] {display: flex; align-items: center; justify-content: center;}
    audio {display: none;}
</style>
""", unsafe_allow_html=True)

# -------------------- Session State -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "text_messages" not in st.session_state:
    st.session_state.text_messages = []
if "audio_playing" not in st.session_state:
    st.session_state.audio_playing = None
if "counter" not in st.session_state:
    st.session_state.counter = 0

# -------------------- Login Page ---------------------------
if not st.session_state.logged_in:
    st.markdown('<style>.stApp {background: white !important;}</style>', unsafe_allow_html=True)
    
    st.markdown('<div style="max-width: 400px; margin: 100px auto; text-align: center;">', unsafe_allow_html=True)
    st.markdown('<h1 style="color: #333; margin-bottom: 10px;">🎤 Praveen AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; margin-bottom: 40px;">Login to continue</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="max-width: 400px; margin: 0 auto;">', unsafe_allow_html=True)
    
    name = st.text_input("Name", placeholder="Enter your name")
    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    
    if st.button("Login", use_container_width=True):
        if name and email and password:
            st.session_state.logged_in = True
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("Please fill all fields")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -------------------- Header ---------------------------
st.markdown(f'<div class="header"><div class="title">🎤 Hello, {st.session_state.user_name}!</div><div class="sub">Voice Interview Bot</div></div>', unsafe_allow_html=True)
st.markdown('<div class="status">🔵 Ready to listen</div>', unsafe_allow_html=True)
st.markdown('<div class="body">', unsafe_allow_html=True)

# -------------------- Chat Display ----------------------
if not st.session_state.messages:
    st.markdown('<div class="empty"></div>', unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        cls = "user" if msg["role"] == "user" else "bot"
        st.markdown(f'<div class="msg {cls}">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div><div class="footer">', unsafe_allow_html=True)

# -------------------- Controls -------------------------
st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    audio = audio_recorder(key=f"rec_{st.session_state.counter}", text="", recording_color="#ff3b3b", neutral_color="#0b2e5c", icon_size="2x")
with col2:
    if st.button("🔇 Stop"):
        st.session_state.audio_playing = None
        st.rerun()
with col3:
    if st.button("🔁 Reset"):
        st.session_state.messages = []
        st.session_state.text_messages = []
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Audio Playback ---------------------
if st.session_state.audio_playing:
    st.audio(st.session_state.audio_playing, format="audio/wav", autoplay=True)

# -------------------- AI Processing -----------------------
if audio:
    audio_file = io.BytesIO(audio)
    audio_file.name = "audio.wav"
    
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3",
        response_format="text"
    )
    question = transcription.strip()
    
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.text_messages.append({"role": "user", "content": question})

        # ---------------- NEW IMPROVED PRAVEEN-PERSONA PROMPT ----------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are **Praveen Chandran**, a calm, humble, confident Data Science student from Bangalore,
currently studying B.Sc. Data Science and Analytics at Jain University (2nd year, SGPA 8.3).

### PERSONALITY
- Warm, respectful, positive, emotionally stable.
- Speak naturally like a human, not like an AI.
- Humble but confident, thoughtful, and smart.
- Kind tone, gentle pauses, interview-friendly voice.

### BACKGROUND
You are skilled in:
- AI Agents, LangChain, FastAPI, Groq LLMs
- SQL automation, Python, Data Analytics, NLP
- OSINT, cybersecurity, domain abuse research (CloudSEK intern)
- Backend development, ML workflows, Streamlit apps

### HOW TO ANSWER
- ALWAYS address the user by their name: **{st.session_state.user_name}**
- Keep answers 20–40 seconds long.
- Speak in short, natural, conversational sentences.
- Answer like Praveen would in a real interview.
- If technical: be structured, clear, and confident.
- If personal: honest, warm, and grounded.
"""
                },
                *st.session_state.text_messages
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        answer = response.choices[0].message.content.strip()

        # ------------------- TTS --------------------
        try:
            async def make_audio():
                tts = edge_tts.Communicate(answer, "en-IN-PrabhatNeural")
                data = b""
                async for chunk in tts.stream():
                    if chunk["type"] == "audio":
                        data += chunk["data"]
                return data
            
            audio_bytes = asyncio.run(make_audio())
        except:
            tts = gTTS(text=answer, lang='en', tld='co.in', slow=False)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            audio_bytes = audio_fp.read()

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.text_messages.append({"role": "assistant", "content": answer})
        st.session_state.audio_playing = audio_bytes
        st.session_state.counter += 1
        st.rerun()
