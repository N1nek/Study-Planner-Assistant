An AI-powered web application for managing academic workload, tracking study sessions, and receiving personalized study recommendations.

Features

Subject Management - Add, view, and delete subjects with difficulty ratings and priority levels

Task Tracking - Create assignments with due dates, mark completion, and organize by status
​
Study Logging - Record study sessions with date, duration, and notes
​
AI Chat Assistant - Get personalized study advice using Google Gemini API

Analytics Dashboard - Visualize study patterns with interactive charts and statistics
​

Tech Stack

Frontend: Streamlit (Python web framework)
Database: SQLite with pandas integration
AI: Google Generative AI (Gemini 2.0 Flash)
Visualization: Plotly for interactive charts

Install dependencies
pip install -r requirements.txt

Run application
streamlit run main.py

Usage
Get API Key - Obtain free Gemini API key from Google AI Studio
Launch App - Run streamlit run main.py and open http://localhost:8501
Configure - Enter API key in sidebar settings
Start Planning - Add subjects, create tasks, log study sessions

Requirements
Python 3.8+
Dependencies listed in requirements.txt
​