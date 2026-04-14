# 🎯 AI Interview Evaluator

An intelligent, AI-powered mock interview platform that helps candidates prepare for job interviews by providing personalized questions, real-time speech-to-text interaction, and detailed performance evaluation.

![Project Preview](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)

## 🚀 Key Features

- **📄 Smart Resume Parsing**: Upload your resume in PDF, DOCX, or TXT format. The system automatically extracts skills, experience duration, and education details.
- **🧠 Personalized Question Generation**: Uses OpenAI's GPT-3.5-Turbo to generate questions tailored specifically to your background and the role you're targeting.
- **🎤 Voice & Text Input**: Answer questions by typing or use the built-in microphone support (powered by Google Speech Recognition) for a more realistic interview experience.
- **📊 Real-time Evaluation**: Get instant feedback on your answers across 5 critical dimensions:
  - **Confidence**: Overall tone and decisiveness.
  - **Clarity**: Structure and coherence of the response.
  - **Positivity**: Enthusiasm and professional outlook.
  - **Relevance**: How well the answer addresses the question.
  - **Professionalism**: Formal language and appropriate tone.
- **📈 Performance Analytics**: Visualize your interview performance with interactive radar charts and detailed score breakdowns.
- **📥 Report Export**: Download a full JSON report of your interview session for further review.

---

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Large Language Model**: OpenAI GPT-3.5-Turbo
- **Speech Recognition**: Google Speech-to-Text via `SpeechRecognition`
- **NLP Utilities**: `Regex`, `PyPDF2`, `python-docx`
- **Visualization**: `Plotly`, `Pandas`

---

## 📂 Project Structure

```text
proj1/
├── main.py                # Main Streamlit application
├── question_generator.py  # GPT-based question generation logic
├── interview_evaluator.py # Scoring and feedback engine
├── resume_parser.py       # PDF/DOCX text extraction and parsing
├── speech_recognizer.py   # Microphone and STT handling
├── .env                   # Environment variables (OpenAI API Key)
└── requirements.txt       # Project dependencies
```

---

## 🔧 Setup & Installation

### 1. Prerequisites
- Python 3.8 or higher
- An OpenAI API Key

### 2. Clone the Repository
```bash
git clone https://github.com/JoyV24/AI-Interviewer.git
cd AI-Interviewer/proj1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: On Windows, you may need to install `pyaudio` for microphone support (`pip install pipwin && pipwin install pyaudio`).*

### 4. Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Application
```bash
streamlit run main.py
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

*Built with ❤️ for better interview preparation.*