# **HR AI Assistant System**

This project is a complete AI-powered HR automation system built using **Streamlit**, **OpenAI**, and **Google Workspace APIs**. It streamlines HR workflows including **resume evaluation, onboarding, automated scheduling, voice-based interviews, and HR policy guidance**.

---

## 🎯 **Objectives**

### ✔ Automate HR Query Handling

* AI-powered HR assistant that responds to policy and workplace-related questions using an LLM.

### ✔ Resume Screening Against Job Description

* Users upload resumes (PDF/DOCX).
* The system extracts content and compares it with a job description.
* AI generates:

  * Skill match %
  * Strengths and weaknesses
  * Hiring recommendation
* Evaluation records are stored in **Google Sheets** (`HR_Agent_Records`).

### ✔ AI-Driven Automated Voice Interview

* Uses microphone input recording via WebRTC.
* Converts speech to text using Google Speech Recognition.
* Performs a **microphone test** before starting the interview.
* Interview begins with **text-to-speech questions** while webcam and microphone stay active.
* Responses are evaluated automatically and stored in Google Sheets.
* The system generates:

  * Interview score
  * Strengths and weaknesses
  * Final verdict (Hire / Consider / Reject)
* Generates downloadable **calendar invite (.ics)** and logs interview details.

### ✔ Employee Onboarding with Calendar Integration

* Collects employee name, email, and joining date.
* AI generates a structured onboarding plan.
* Stores onboarding data in **Google Sheets**.
* Schedules tasks in **Google Calendar**.

### ✔ Smart Scheduling System

* Create tasks, events, appointments, or interview schedules.
* Automatically generates Google Calendar entries with optional attendee emails.

---

## 🌟 **Features**

* AI-powered HR question answering
* Resume parsing, scoring, and automated hiring recommendation
* Automated voice interview with speech-to-text evaluation
* Onboarding automation with Google Calendar integration
* Smart task scheduling with event reminders
* Secure storage in Google Sheets
* Text-to-speech and microphone validation system
* Interactive Streamlit interface

---

## ⚠️ **Limitations**

* Accuracy of resume and interview scoring depends on input quality and AI model limits
* Requires stable internet connection for OpenAI and Google APIs
* Speech recognition may struggle with accents or background noise
* Google API authorization must be configured manually before first use
* Supports PDF and DOCX resume formats only
* No multi-user authentication implemented (single admin mode)

---

## 🛠️ **Tech Stack & APIs Used**

| Component         | Technology / API Used      |
| ----------------- | -------------------------- |
| Frontend UI       | Streamlit                  |
| Backend           | Python                     |
| AI Model          | OpenAI                     |
| Cloud Services    | Google Workspace APIs      |
| Speech Processing | SpeechRecognition + WebRTC |
| Text-to-Speech    | gTTS                       |
| File Processing   | PyPDF2, docx2txt           |

---

## 📁 **Project Structure**

```
📂 HR_AI_Assistant
│── app.py
│── .env
│── service_account.json
│── requirements.txt
│── README.md
│── hr_data.txt
│── question.mp3
```

---

## 🔑 **Required Configuration**

### 1️⃣ Environment File (`.env`)

```
OPENAI_API_KEY=your_api_key
```

### 2️⃣ Google Setup Requirements

* Enable Google Sheets API, Google Drive API, Google Calendar API
* Create a spreadsheet named `HR_Agent_Records` with worksheets:

  * Onboarding
  * Resume_Screening
  * Interviews
* Share the sheet with the **service account email**
* Place `service_account.json` in the project folder

---

## ▶️ **How to Run**

```sh
pip install -r requirements.txt
streamlit run app.py
```

Once executed, the Streamlit interface will open automatically.

---

## 📦 **Dependencies**

```
streamlit
openai
python-dotenv
PyPDF2
docx2txt
SpeechRecognition
numpy
streamlit-webrtc
av
gTTS
google-auth
google-auth-oauthlib
google-api-python-client
gspread
pydub
```

---

## 💡 **Potential Improvements**

* Add user authentication (OAuth login / admin panel)
* Support additional resume formats (image, text scraping, LinkedIn import)
* Improve AI evaluation with fine-tuned HR models
* Add analytics dashboard (candidate performance, hiring insights)
* Automate email notifications (offer letters, reminders)
* Multilingual speech & response support
* Deploy on cloud for persistent storage & scalable usage


