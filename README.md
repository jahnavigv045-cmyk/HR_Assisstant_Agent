 HR AI Assistant System

This project is a complete AI-powered HR automation system built using **Streamlit**, **OpenAI**, and **Google Workspace APIs**. It streamlines the recruitment and HR workflow, including resume evaluation, onboarding, automated scheduling, voice-based interviews, and HR policy guidance.

 Objectives

The primary objectives of this project are:

1. **Automate HR Query Handling**

   * Implement an AI-powered HR assistant that provides instant responses to HR policy and workplace-related questions using an OpenAI model.

2. **Resume Screening Against Job Description**

   * Enable users to upload resumes (PDF/DOCX) which the system extracts text from.
   * Compare candidate resume with job description using AI and generate:

     * Skill Match %
     * Strengths & weaknesses
     * Final hiring recommendation.
   * Automatically log evaluation records into Google Sheets.(google sheet Name :HR_Agent_Records)

3. **AI-Driven Automated Voice Interview**

   * Conduct structured voice interviews using:

     * Microphone input recording via WebRTC.
     * Speech-to-Text using Google Speech Recognition.
     * first test the microphone working in user laptop ,if user pass in microphone voice test then it is ready to give interview
     * when it click start interview it starts the interview by displaying question with voice of text to voice conversion of qiuestion
     * webcam and microphone is on and user answers where model records the voice and evalutes and give result and stored in google sheets (google sheet Name :HR_Agent_Records)
   * AI evaluates response quality and provides:

     * Score
     * Strengths
     * Weaknesses
     * Final verdict (Hire / Consider / Reject)
   * Generate and download an interview calendar invite (.ics) and log interview records in Google Sheets.

4. **Employee Onboarding with Calendar Integration**

   * Automatically generate an onboarding plan for the new employee using AI. takes Name and email and date 
   * Store onboarding details in Google Sheets.(google sheet Name :HR_Agent_Records)
   * Schedule onboarding tasks directly into Google Calendar.

5. **Smart Scheduling System**

   * Allow creating tasks, events, appointments, and interview schedules.
   * Automatically generate Google Calendar entries, including optional attendee emails.

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit (UI)**
* **OpenAI API**
* **Google Workspace API (Sheets + Calendar)**
* **SpeechRecognition + WebRTC**
* **gTTS for Text-to-Speech**

---

## 📁 Project Structure

```
📂 HR_AI_Assistant
│── app.py
│── .env
│── service_account.json
│── requirements.txt
│── README.md
```

---

## 🔑 Required Configuration

### Environment File (`.env`)

```
OPENAI_API_KEY=your_api_key
```

### Google Setup Requirements

Enable the following Google services:

* Google Sheets API
* Google Drive API
* Google Calendar API

Create a sheet named:

```
HR_Agent_Records
```

With worksheets:

* Onboarding
* Resume_Screening
* Interviews

Share it with the service account email.

Place the downloaded `service_account.json` in the project folder.

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```
if u run this the streamlit will be opened


Requirements needed to run the code 

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

---

