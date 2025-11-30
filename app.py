import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import PyPDF2
import docx2txt
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import numpy as np
import av
from gtts import gTTS
import time

# ------------------- LOAD API KEYS --------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI API Key Missing! Please update .env file.")
    st.stop()
client = OpenAI(api_key=api_key)

# ------------------- GOOGLE SHEETS SETUP ---------------
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json

gc = None
sheet_onboarding = None
sheet_resume = None
sheet_interview = None

try:
    # Check if running on Streamlit Cloud
    if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
        # Use secrets for cloud deployment
        google_creds = st.secrets["google_service_account"]
        creds = Credentials.from_service_account_info(google_creds)
        gc = gspread.authorize(creds)
    else:
        # Local mode, use local JSON file
        gc = gspread.service_account(filename="service_account.json")

    # Open sheets
    sheet_onboarding = gc.open("HR_Agent_Records").worksheet("Onboarding")
    sheet_resume = gc.open("HR_Agent_Records").worksheet("Resume_Screening")
    sheet_interview = gc.open("HR_Agent_Records").worksheet("Interviews")

except Exception as e:
    st.warning("⚠ Google Sheets not available or worksheets missing. Continue without Sheets logging.")

# ------------------- GOOGLE CALENDAR SETUP -------------
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
calendar_service = build('calendar', 'v3', credentials=creds)

def create_calendar_entry(title, description, start_dt=None, duration_hours=1, attendee_email=None, type='event'):
    if type == 'task':
        event_body = {
            'summary': f"Task: {title}",
            'description': description,
            'start': {'date': datetime.today().date().isoformat()},
            'end': {'date': datetime.today().date().isoformat()},
        }
    else:
        end_dt = start_dt + timedelta(hours=duration_hours)
        event_body = {
            'summary': f"{type.title()}: {title}",
            'description': description,
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
        }
        if attendee_email:
            event_body['attendees'] = [{'email': attendee_email}]
    created_event = calendar_service.events().insert(calendarId='primary', body=event_body).execute()
    return created_event.get('htmlLink')

# ------------------- AI RESPONSE FUNCTION ----------------
def ai_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# -------------------------- STREAMLIT UI -------------------------
st.set_page_config(layout="wide", page_title="🤖 HR AI Assistant Suite", page_icon="🧑‍💼")
st.markdown("<h1 style='text-align:center; color:#4B0082;'>🤖 HR AI Agent System</h1>", unsafe_allow_html=True)

tabs = st.tabs([
    "🧭 HR Assistant",
    "📄 Resume Screening",
    "🎤 AI Interview",
    "📝 Employee Onboarding",
    "📅 Schedule Task/Event/Appointment"
])

# ------------------- TAB 1: HR ASSISTANT -----------------
with tabs[0]:
    st.subheader("🧭 HR Policy & FAQ Agent", anchor="hr_assistant")
    question = st.text_input("💬 Ask any HR policy or workplace question:", key="hr_question")
    if st.button("🟢 Get Answer", key="hr_btn", help="Click to get AI answer"):
        if question.strip() != "":
            reply = ai_response(f"Answer like an HR assistant: {question}")
            st.success(f"✅ Answer: {reply}", icon="✅")
        else:
            st.error("⚠ Please type a question first.", icon="⚠️")

# ------------------- TAB 2: RESUME SCREENING -----------------
with tabs[1]:
    st.subheader("📄 Resume Screening Against Job Description", anchor="resume_screen")
    job_desc = st.text_area("📝 Paste Job Description", key="job_desc")
    uploaded_file = st.file_uploader("📂 Upload Resume (.pdf / .docx)", type=["pdf", "docx"], key="resume_file")
    cand_name = st.text_input("👤 Candidate Name", key="resume_name")
    cand_email = st.text_input("📧 Candidate Email", key="resume_email")

    if st.button("🟢 Analyze Resume", key="resume_btn") and uploaded_file:
        text = ""
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = docx2txt.process(uploaded_file)

        prompt = f"""
Compare this resume with the job description. Return a clean evaluation report:

Candidate Name: {cand_name}
Candidate Email: {cand_email}
Job Description: {job_desc}
Resume Content: {text}

Include:
- Skill Match %
- Strengths
- Missing Skills
- Experience Fit
- Final Verdict (Hire / Consider / Reject)
- Short Summary
"""
        result = ai_response(prompt)
        st.success(f"📊 Evaluation Result:\n{result}")
        if sheet_resume:
            try:
                sheet_resume.append_row([cand_name, cand_email, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), result])
            except Exception as e:
                st.warning(f"⚠ Could not save resume result: {e}")

# ------------------- TAB 3: AI INTERVIEW -----------------
with tabs[2]:
    st.subheader("🎤 Voice-Based AI Interview System", anchor="ai_interview")

    candidate_name = st.text_input("👤 Candidate Name", key="cand_name")
    candidate_email = st.text_input("📧 Candidate Email", key="cand_email")
    role_applied = st.text_input("💼 Job Role", key="cand_role")

    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "question" not in st.session_state:
        st.session_state.question = None
    if "question_number" not in st.session_state:
        st.session_state.question_number = 1
    if "last_eval" not in st.session_state:
        st.session_state.last_eval = ""
    if "mic_test_passed" not in st.session_state:
        st.session_state.mic_test_passed = False
    if "mic_test_text" not in st.session_state:
        st.session_state.mic_test_text = ""

    st.markdown("### 🎤 Microphone Test (Before Starting Interview)")

    class MicTestProcessor:
        def __init__(self):
            self.audio = None
        def recv_audio(self, frame: av.AudioFrame):
            arr = frame.to_ndarray()
            if arr.ndim > 1:
                arr = arr.mean(axis=0).astype(np.int16)
            self.audio = arr
            return frame

    mic_test_processor = MicTestProcessor()
    mic_test_ctx = webrtc_streamer(
    key="mic_test",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=lambda: mic_test_processor,
    media_stream_constraints={
        "audio": {
            "deviceId": "default",
            "echoCancellation": True,
            "noiseSuppression": True,
            "autoGainControl": True,
            "advanced": [
                {"echoCancellation": True},
                {"noiseSuppression": True},
                {"autoGainControl": True}
            ]
        },
        "video": False
    },
    async_processing=True
)



    st.info("💡 Speak something like: 'Testing microphone, one two three'")

    if st.button("🟢 Test Microphone"):
        if mic_test_processor.audio is None:
            st.error("❌ No audio detected! Please check your microphone settings.")
        else:
            try:
                recognizer = sr.Recognizer()
                audio_data = sr.AudioData(mic_test_processor.audio.tobytes(), sample_rate=48000, sample_width=2)
                transcript = recognizer.recognize_google(audio_data)
                st.session_state.mic_test_text = transcript
                st.success(f"🎉 Microphone works! You said: **{transcript}**")
                st.session_state.mic_test_passed = True
            except Exception as e:
                st.error(f"⚠ Error reading microphone: {e}")
                st.session_state.mic_test_passed = False

    if not st.session_state.mic_test_passed:
        st.warning("⚠ Please complete microphone test before starting the interview.")

    if st.button("🟢 Start Interview") and st.session_state.mic_test_passed:
        if not role_applied.strip():
            st.error("⚠ Enter job role first.")
        else:
            st.session_state.interview_started = True
            st.session_state.question_number = 1
            st.session_state.question = ai_response(f"Generate ONLY the first interview question for {role_applied}. Make it technical and role specific.")
            st.success("✅ Interview Started!")

            # ---- Add downloadable calendar invite ----
            interview_start = datetime.now().strftime("%Y%m%dT%H%M%S")
            interview_end = (datetime.now() + timedelta(minutes=30)).strftime("%Y%m%dT%H%M%S")
            ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:AI Interview - {candidate_name}
DTSTART:{interview_start}
DTEND:{interview_end}
DESCRIPTION:Interview scheduled for role {role_applied}.
ORGANIZER;CN=HR AI Agent:mailto:{candidate_email}
END:VEVENT
END:VCALENDAR"""
            st.download_button(
                label="📥 Download Interview Invite (.ics)",
                data=ics_content,
                file_name=f"{candidate_name}_Interview.ics",
                mime="text/calendar"
            )

    # Function to speak text
    def speak_text(text):
        tts = gTTS(text, lang="en", tld="co.in")
        tts.save("question.mp3")
        audio_file = open("question.mp3", "rb").read()
        st.audio(audio_file, format="audio/mp3")

    if st.session_state.interview_started and st.session_state.question:
        st.markdown(f"### 📝 Question {st.session_state.question_number}")
        st.write(st.session_state.question)
        speak_text(st.session_state.question)
        st.warning("🎙 Please speak your answer. Recording is active...")

        class AudioProcessor:
            def __init__(self):
                self.audio = None
            def recv_audio(self, frame: av.AudioFrame):
                arr = frame.to_ndarray()
                if arr.ndim > 1:
                    arr = arr.mean(axis=0).astype(np.int16)
                self.audio = arr
                return frame

        audio_processor = AudioProcessor()
        cctx = webrtc_streamer(
    key=f"audio_{st.session_state.question_number}",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=lambda: audio_processor,
    media_stream_constraints={
        "audio": {
            "deviceId": "default",
            "echoCancellation": True,
            "noiseSuppression": True,
            "autoGainControl": True,
            "advanced": [
                {"echoCancellation": True},
                {"noiseSuppression": True},
                {"autoGainControl": True}
            ]
        },
        "video": False
    },
    async_processing=True
)



        if st.button("🟢 Submit Answer"):
            if audio_processor.audio is None:
                st.error("⚠ No voice detected! Please speak again.")
            else:
                try:
                    rec = sr.Recognizer()
                    audio_data = sr.AudioData(audio_processor.audio.tobytes(), sample_rate=48000, sample_width=2)
                    transcript = rec.recognize_google(audio_data)
                    st.info(f"🗣 You Said: {transcript}")

                    evaluation = ai_response(f"""
Evaluate this candidate's response for role {role_applied}.
Question: {st.session_state.question}
Answer: {transcript}
Return:
- Score (0-10)
- Strengths
- Weaknesses
- Final Verdict (Hire / Consider / Reject)
""")
                    st.success(evaluation)
                    st.session_state.last_eval = evaluation

                    if sheet_interview:
                        try:
                            sheet_interview.append_row([candidate_name, candidate_email, role_applied,
                                                        st.session_state.question, transcript, evaluation,
                                                        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")])
                        except:
                            pass

                    if st.session_state.question_number < 5:
                        st.session_state.question_number += 1
                        st.session_state.question = ai_response(f"Generate the next interview question for {role_applied}. Avoid repeating previous topics.")
                        st.experimental_rerun()
                    else:
                        st.success("✅ Interview Completed. Maximum 5 questions reached.")

                except Exception as e:
                    st.error(f"❌ Error processing audio: {e}")

    if st.session_state.last_eval:
        st.markdown("### 🧾 Last Evaluation")
        st.write(st.session_state.last_eval)

# ------------------- TAB 4: EMPLOYEE ONBOARDING -----------------
with tabs[3]:
    st.subheader("📝 Employee Onboarding")
    name = st.text_input("👤 Full Name", key="onb_name")
    email = st.text_input("📧 Email", key="onb_email")
    role = st.text_input("💼 Job Role", key="onb_role")
    joining_date = st.date_input("📅 Joining Date", key="onb_date")

    if st.button("🟢 Generate Onboarding Plan", key="onb_btn"):
        if not name or not email or not role or not joining_date:
            st.error("⚠ Please fill all fields.")
        else:
            instructions = ai_response(f"Create a complete onboarding plan for new employee: {name}, role: {role}.")
            st.info(instructions)
            if sheet_onboarding:
                try:
                    sheet_onboarding.append_row([name, email, role, str(joining_date), "Onboarding Started"])
                    st.success("✅ Saved to Google Sheet")
                except Exception as e:
                    st.error(f"❌ Failed to save to Google Sheet: {e}")
            try:
                link = create_calendar_entry(name, f"Onboarding for {role}", start_dt=datetime.combine(joining_date, datetime.min.time()), type='event')
                st.success(f"✅ Onboarding scheduled: [Open Event]({link})")
            except Exception as e:
                st.error(f"❌ Failed to create calendar event: {e}")

# ------------------- TAB 5: TASK/EVENT/APPOINTMENT -----------------
with tabs[4]:
    st.subheader("📅 Schedule Task / Event / Appointment")
    sched_type = st.selectbox("📌 Type", ["Task", "Event", "Appointment"], key="sched_type")
    title = st.text_input("📝 Title", key="sched_title")
    description = st.text_area("📝 Description", key="sched_desc")
    if sched_type != "Task":
        date_input = st.date_input("📅 Date", key="sched_date")
        time_input = st.time_input("⏰ Time", key="sched_time")
        start_dt = datetime.combine(date_input, time_input)
    else:
        start_dt = None
    attendee_email = st.text_input("📧 Attendee Email (optional)", key="sched_email")

    if st.button("🟢 Create Schedule", key="sched_btn"):
        try:
            link = create_calendar_entry(title, description, start_dt=start_dt, attendee_email=attendee_email, type=sched_type.lower())
            st.success(f"✅ {sched_type} created: [Open Event]({link})")
        except Exception as e:
            st.error(f"❌ Failed to create {sched_type}: {e}")
