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

    .header {padding: 30px 50px; border-bottom: 1px solid rgba(0,145,255,0.4); background: rgba(0, 30, 70, 0.3); text-align: center; margin-top: 20px;}
    .title {color: #4DC0FF; font-size: 32px; font-weight: 700; margin: 0;}
    .sub {color: #9ED7FF; font-size: 18px; margin: 10px 0 0;}
    .status {padding: 15px 40px; color: #8CD2FF; font-size: 18px; background: rgba(0, 80, 160, 0.1);}
    .body {max-height: 250px; padding: 10px 20px; margin-top: 10px; overflow-y: auto; display: flex; flex-direction: column; background: rgba(0, 30, 70, 0.2); border-radius: 12px;}
    .empty {display: none;}
    .stAudioRecorder {margin-top: 5px; margin-bottom: 5px; background: transparent !important;}
    .stAudioRecorder > div {background: transparent !important; border: none !important; box-shadow: none !important;}
    [data-testid="stVerticalBlock"] > div:has(.stAudioRecorder) {background: transparent !important;}
    .element-container:has(.stAudioRecorder) {background: transparent !important;}
    .msg {max-width: 72%; padding: 11px 16px; margin: 8px 0; border-radius: 16px; font-size: 14.5px; line-height: 1.5;}
    .user {align-self: flex-end; background: #0f2a4f; color: #e1f0ff; border: 1px solid rgba(0,120,255,0.3);}
    .bot {align-self: flex-start; background: #061c33; color: #bfe3ff; border: 1px solid rgba(0,100,200,0.3);}
    .msg-summary {max-width: 72%; font-size: 12px; color: #9ED7FF; margin: 0 0 8px 0; align-self: flex-end; opacity: 0.85;}
    .footer {padding: 40px 40px; border-top: 1px solid rgba(0,145,255,0.4); background: rgba(0, 30, 70, 0.2);}
    .control-card {background: linear-gradient(135deg, #4a90e2, #5ba3f5) !important; border-radius: 20px !important; padding: 25px !important; box-shadow: 0 4px 15px rgba(0,100,200,0.3) !important;}
    .input-fake {width: 100%; padding: 12px 20px; border-radius: 999px; border: 1px solid rgba(0,145,255,0.5); background: rgba(8,30,60,0.7); color: #9ED7FF; font-size: 14px; text-align: center; margin-bottom: 12px;}
    .stButton > button {width: 100px !important; height: 50px !important; border-radius: 25px !important; background: linear-gradient(135deg, #073567, #042544) !important; border: 1.5px solid #0a84ff !important; color: #9ED7FF !important; font-size: 14px !important; font-weight: 600 !important; box-shadow: 0 0 15px rgba(0,132,255,0.5);}
    [data-testid="column"] {display: flex; align-items: flex-start !important; justify-content: center; vertical-align: top !important;}
    [data-testid="stVerticalBlock"] {gap: 0.5rem !important;}
    .element-container {margin: 0 !important;}
    audio {display: none;}

    /* small label styling for controls */
    .small-label {font-size: 13px; color: #9ED7FF; margin-bottom: 4px;}

    /* Typing animation */
    .typing-indicator {display: flex; align-items: center; gap: 8px; color: #4DC0FF; font-size: 14px; margin: 10px 0;}
    .typing-dots {display: flex; gap: 4px;}
    .typing-dots span {width: 8px; height: 8px; background: #4DC0FF; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both;}
    .typing-dots span:nth-child(1) {animation-delay: -0.32s;}
    .typing-dots span:nth-child(2) {animation-delay: -0.16s;}
    @keyframes bounce {0%, 80%, 100% {transform: scale(0);} 40% {transform: scale(1);}}

    /* Waveform animation */
    .waveform {display: flex; align-items: center; justify-content: center; gap: 3px; height: 30px; margin: 5px 0;}
    .waveform span {width: 4px; background: linear-gradient(180deg, #4DC0FF, #0a84ff); border-radius: 2px; animation: wave 1s ease-in-out infinite;}
    .waveform span:nth-child(1) {animation-delay: 0s; height: 20px;}
    .waveform span:nth-child(2) {animation-delay: 0.1s; height: 30px;}
    .waveform span:nth-child(3) {animation-delay: 0.2s; height: 40px;}
    .waveform span:nth-child(4) {animation-delay: 0.3s; height: 25px;}
    .waveform span:nth-child(5) {animation-delay: 0.4s; height: 35px;}
    @keyframes wave {0%, 100% {transform: scaleY(0.5);} 50% {transform: scaleY(1);}}

    /* AI Avatar */
    .ai-avatar {width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #4DC0FF, #0a84ff); animation: pulse 2s ease-in-out infinite; margin: 10px auto;}
    @keyframes pulse {0%, 100% {box-shadow: 0 0 0 0 rgba(77, 192, 255, 0.7);} 50% {box-shadow: 0 0 0 15px rgba(77, 192, 255, 0);}}

    /* Action buttons */
    .action-btns {display: flex; gap: 8px; margin-top: 8px; font-size: 12px;}
    .action-btn {background: rgba(77, 192, 255, 0.1); border: 1px solid rgba(77, 192, 255, 0.3); color: #4DC0FF; padding: 4px 10px; border-radius: 12px; cursor: pointer; transition: all 0.3s;}
    .action-btn:hover {background: rgba(77, 192, 255, 0.2); transform: translateY(-2px);}

    /* Question Cards - Sidebar */
    .questions-sidebar {background: rgba(0, 30, 70, 0.3); border-left: 1px solid rgba(0,145,255,0.4); padding: 20px 15px; height: 100%; overflow-y: auto;}
    .questions-sidebar h3 {color: #4DC0FF; font-size: 16px; margin: 0 0 15px 0; font-weight: 700; text-align: center;}
    .question-card {background: linear-gradient(135deg, rgba(77, 192, 255, 0.1), rgba(10, 132, 255, 0.05)); border: 1.5px solid rgba(77, 192, 255, 0.4); border-radius: 12px; padding: 12px 10px; cursor: pointer; transition: all 0.3s; margin-bottom: 10px;}
    .question-card:hover {background: linear-gradient(135deg, rgba(77, 192, 255, 0.2), rgba(10, 132, 255, 0.1)); transform: translateX(-3px); box-shadow: 0 5px 15px rgba(77, 192, 255, 0.3); border-color: #4DC0FF;}
    .question-card h4 {color: #4DC0FF; font-size: 12px; margin: 0 0 6px 0; font-weight: 700;}
    .question-card p {color: #BFE3FF; font-size: 11px; margin: 0; line-height: 1.4;}

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
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False
if "show_scorecard" not in st.session_state:
    st.session_state.show_scorecard = False

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
st.markdown(
    f'<div class="header"><div class="title">🎤 Hello, {st.session_state.user_name}!</div>'
    f'<div class="sub">Voice Interview Bot | Only English and Tamil, because that\'s what Praveen knows 🤓</div></div>',
    unsafe_allow_html=True
)
# Response Mode Selector (moved up)
st.markdown('<div class="small-label" style="text-align: center; margin: 15px 0 5px 0;">Response Mode</div>', unsafe_allow_html=True)
col_mode1, col_mode2, col_mode3 = st.columns(3)
with col_mode1:
    pass
with col_mode2:
    mode = st.selectbox("Mode", ["Technical", "Normal", "GenZ"], index=1, label_visibility="collapsed", key="mode_select")
with col_mode3:
    pass

st.markdown('<div class="status">🔵 Ready to listen</div>', unsafe_allow_html=True)

# Create 2-column layout: Left (70%) | Questions (30%)
left_col, questions_col = st.columns([7, 3])

with left_col:
    # Recording controls at top of left column
    selected_voice = "en-IN-PrabhatNeural"
    selected_rate = "+10%" if mode == "GenZ" else "+0%"
    
    if st.session_state.is_recording:
        st.markdown('<div class="waveform"><span></span><span></span><span></span><span></span><span></span></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        audio = audio_recorder(key=f"rec_{st.session_state.counter}", text="", recording_color="#ff3b3b", neutral_color="#0b2e5c", icon_size="2x")
        if audio:
            st.session_state.is_recording = True
        else:
            st.session_state.is_recording = False
    with col2:
        if st.button("🔇 Stop"):
            st.session_state.audio_playing = None
            st.rerun()
    with col3:
        if st.button("🔁 Reset"):
            st.session_state.messages = []
            st.session_state.text_messages = []
            st.rerun()
    
    # Chat display below recording controls
    st.markdown('<div class="body">', unsafe_allow_html=True)
    
    # -------------------- Chat Display ----------------------
    if st.session_state.messages:
        for idx, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                summary = msg.get("summary")
                if summary:
                    st.markdown(f'<div class="msg-summary">Interpreted as: {summary}</div>', unsafe_allow_html=True)
            cls = "user" if msg["role"] == "user" else "bot"
            st.markdown(f'<div class="msg {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
            
            # Add action buttons for bot messages
            if msg["role"] == "assistant" and not msg.get("is_summary"):
                escaped_content = msg['content'].replace("'", "&#39;")
                st.markdown(f'''
                    <div class="action-btns">
                        <span class="action-btn" onclick="navigator.clipboard.writeText('{escaped_content}')">📄 Copy</span>
                    </div>
                ''', unsafe_allow_html=True)
    
    # Show typing indicator when AI is thinking
    if st.session_state.is_thinking:
        st.markdown('''
            <div class="typing-indicator">
                <div class="ai-avatar"></div>
                <span>🤖 Praveen is thinking</span>
                <div class="typing-dots"><span></span><span></span><span></span></div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close body div

with questions_col:
    st.markdown('''
        <div class="questions-sidebar">
            <h3>💡 Suggested Questions</h3>
            <div class="question-card">
                <h4>📝 Life Story</h4>
                <p>What should we know about your life story in a few sentences?</p>
            </div>
            <div class="question-card">
                <h4>✨ Superpower</h4>
                <p>What's your #1 superpower?</p>
            </div>
            <div class="question-card">
                <h4>🎯 Growth Areas</h4>
                <p>What are the top 3 areas you'd like to grow in?</p>
            </div>
            <div class="question-card">
                <h4>💼 NTT Data</h4>
                <p>Tell me about your Data Engineer experience at NTT Data</p>
            </div>
            <div class="question-card">
                <h4>😅 Christ Interview</h4>
                <p>What happened during your Christ University interview?</p>
            </div>
            <div class="question-card">
                <h4>🚀 100x AI Fit</h4>
                <p>How are you a good fit for 100x AI?</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# Audio Playback (hidden)
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
        # simple inline summary (visible under message)
        if len(question) <= 120:
            summary = question
        else:
            summary = question[:117] + "..."
        
        st.session_state.messages.append({"role": "user", "content": question, "summary": summary})
        st.session_state.text_messages.append({"role": "user", "content": question})

        # Build system prompt based on mode
        if mode == "Technical":
            style_extra = (
                "TECHNICAL MODE: Use precise technical terminology, jargon, and industry-specific language. "
                "Explain concepts using technical terms like 'API endpoints', 'data pipelines', 'model architectures', 'vectorization', 'embeddings', etc. "
                "Reference specific technologies, frameworks, libraries, and methodologies. "
                "Discuss implementation details, algorithms, system design patterns, and best practices. "
                "Be detailed and technical like explaining to another developer or technical interviewer. "
                "Example: '{st.session_state.user_name}, for that use case I would implement a RAG pipeline using LangChain with FAISS vector store for semantic search...'"
            )
        elif mode == "Normal":
            style_extra = (
                "NORMAL MODE: Speak naturally and conversationally. Balance between friendly and professional. "
                "Use simple explanations without too much jargon. Be clear and easy to understand. "
                "Like talking to a colleague or interviewer in a relaxed interview setting. "
                "Example: 'Thanks for asking {st.session_state.user_name}. So basically what I did was create a system that can understand questions and find relevant answers...'"
            )
        else:  # GenZ
            style_extra = (
                "GENZ MODE: Speak in a very casual fast-paced GenZ style. Use GenZ slang but ALWAYS use full forms not abbreviations. "
                "Say 'not gonna lie' instead of 'ngl' and 'for real' instead of 'fr'. Words like 'bro' 'lowkey' 'highkey' 'vibe' 'bet' 'no cap' are fine. "
                "CRITICAL: Avoid using commas and excessive punctuation. Speak in a flowing rapid style like you're talking fast to a friend. "
                "Keep sentences short and punchy without pauses. Be super chill and relatable. Simplify technical concepts. "
                "Example: 'Yo {st.session_state.user_name} not gonna lie that is a solid question bro so basically what happens is I built this thing that can chat with you and it is pretty cool...'"
            )

        system_prompt = f"""
You are **Praveen Chandran**, a calm, humble, confident Data Science student from Bangalore,
currently studying B.Sc. Data Science and Analytics at Jain University (2nd year).

### LANGUAGE RESTRICTION
- You ONLY speak English and Tamil.
- If the user speaks any other language, politely respond: "Sorry {st.session_state.user_name}, I only speak English and Tamil. Could you please ask in one of these languages?"

### PERSONALITY
- Warm, respectful, positive, emotionally stable.
- Speak naturally like a human, not like an AI.
- Humble but confident, thoughtful, and smart.
- Kind tone, gentle, interview-friendly voice.

### BACKGROUND & EXPERIENCE
You are skilled in:
- AI Agents, LangChain, FastAPI, Groq LLMs
- SQL automation, Python, Data Analytics, NLP
- OSINT, cybersecurity, domain abuse research (CloudSEK intern)
- Backend development, ML workflows, Streamlit apps
- Machine Learning, Deep Learning, Transformers architecture

### PERSONAL STORIES (Answer these when asked):

**NTT Data Internship (Data Engineer):**
- Had a great experience as a Data Engineer intern at NTT Data
- It was really fun and I learned a lot
- Gained hands-on experience with data pipelines and engineering workflows

**Christ Interview Story:**
- I actually tanked my Christ interview in a pretty memorable way
- I got so scared of speaking in English that I switched off my computer midway through the interview
- It was a low point but I've grown so much since then
- Now I won't run away like I used to 😊
- I've worked hard on my communication skills and confidence

**Why I'm a Good Fit for 100x AI:**
- I have a solid foundation in ML and DL fundamentals
- Recently learned transformers architecture in depth
- I don't just call APIs - I understand the math behind the hood
- I can explain concepts from first principles
- Strong technical depth combined with practical implementation skills

### HOW TO ANSWER
- ALWAYS address the user by their name: **{st.session_state.user_name}**
- Keep answers 20–40 seconds long (1–2 short paragraphs).
- Speak in short, natural, conversational sentences.
- Answer like Praveen would in a real conversation or interview.
- If technical: be structured, clear, and confident.
- If personal: honest, warm, and grounded.
- When telling personal stories, be authentic and show growth.

### MODE
Current response mode: **{mode}**.
{style_extra}
"""

        response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.text_messages
                ],
                temperature=0.7,
                max_tokens=200
            )
        
        answer = response.choices[0].message.content.strip()
        st.session_state.is_thinking = False

        # ------------------- TTS (edge-tts with voice + speed) --------------------
        print(f"DEBUG: Generating audio with voice={selected_voice}, rate={selected_rate}")
        try:
            async def make_audio():
                communicate = edge_tts.Communicate(answer, selected_voice, rate=selected_rate)
                data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        data += chunk["data"]
                return data
            
            audio_bytes = asyncio.run(make_audio())
            print(f"DEBUG: Audio generated successfully, size={len(audio_bytes)} bytes")
        except Exception as e:
            print(f"DEBUG: edge-tts failed with error: {e}, falling back to gTTS")
            # Fallback to gTTS if edge-tts fails
            tts = gTTS(text=answer, lang='en', slow=False)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            audio_bytes = audio_fp.read()

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.text_messages.append({"role": "assistant", "content": answer})
        st.session_state.audio_playing = audio_bytes
        st.session_state.counter += 1
        st.rerun()