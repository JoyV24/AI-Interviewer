from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from transformers import pipeline
import torch
from typing import List, Dict, Tuple
import PyPDF2
import docx
from io import BytesIO
from question_generator import QuestionGenerator
from resume_parser import ResumeParser
from interview_evaluator import InterviewEvaluator
import os
from speech_recognizer import SpeechRecognizer

if "speech_rec" not in st.session_state:
    st.session_state.speech_rec = SpeechRecognizer()

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}

    
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

# Page configuration
st.set_page_config(
    page_title="AI Interview Evaluator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2e8b57;
        padding-bottom: 0.5rem;
    }
    .score-card {
        background-color: #f0f2f6
        color: #333333;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .question-box {
        background-color: #e8f4fd;  /* Existing light blue background */
        color: #333333;             /* ADDED: Dark gray text color for readability */
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #1f77b4; /* Existing blue border */
    }
    .answer-box {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #ccc;
    }
</style>
""", unsafe_allow_html=True)

def create_score_visualization(evaluations):
    """Create interactive score visualization"""
    # Handle both single evaluation and aggregated scores
    if isinstance(evaluations, dict) and 'average' in next(iter(evaluations.values()), {}):
        # This is aggregated data from all_scores
        categories = list(evaluations.keys())
        scores = [evaluations[cat]['average'] for cat in categories]
    else:
        # This is individual evaluation data
        categories = list(evaluations.keys())
        scores = [evaluations[cat]['score'] for cat in categories]
    
    # Ensure proper formatting for display
    categories = [cat.replace('_', ' ').title() for cat in categories]
    
    # Create radar chart
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Interview Performance',
        line=dict(color='#1f77b4', width=3),
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickmode='linear',
                tick0=0,
                dtick=2
            )),
        showlegend=True,
        title="Interview Performance Radar Chart",
        height=400,
        font=dict(size=12)
    )
    
    return fig

def main():
    # Main header
    st.markdown('<h1 class="main-header"> AI Interview Evaluator</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'evaluations' not in st.session_state:
        st.session_state.evaluations = {}
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        [" Upload Resume", " Generate Questions", " Answer Questions", " View Results"]
    )
    
    # Initialize components
    resume_parser = ResumeParser()
    question_generator = QuestionGenerator(api_key)
    evaluator = InterviewEvaluator(api_key)
    
    if page == " Upload Resume":
        st.markdown('<div class="section-header">Upload Your Resume</div>', unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )
        
        if uploaded_file is not None:
            # Extract text based on file type
            if uploaded_file.type == "application/pdf":
                resume_text = resume_parser.extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = resume_parser.extract_text_from_docx(uploaded_file)
            else:  # txt file
                resume_text = str(uploaded_file.read(), "utf-8")
            
            if resume_text:
                # Parse resume content
                st.session_state.resume_data = resume_parser.parse_resume_content(resume_text)
                
                st.success("✅ Resume uploaded and processed successfully!")
                
                # Display extracted information
                col1, col2 = st.columns(2)
                
                # In the "Upload Resume" section:
                with col1:
                    st.subheader(" Extracted Skills")
                    if st.session_state.resume_data['skills']:
                        for skill in st.session_state.resume_data['skills']:
                            st.markdown(f"<span class='badge'>{skill}</span>", 
                                    unsafe_allow_html=True)
                    else:
                        st.info("No specific skills detected")
                
                with col2:
                    st.subheader(" Profile Summary")
                    st.metric("Experience", f"{st.session_state.resume_data['experience_years']} years")
                    if st.session_state.resume_data['education']:
                        st.write("**Education:** " + ", ".join(st.session_state.resume_data['education']))
                
                # Preview resume text
                with st.expander(" View Extracted Resume Text"):
                    st.text_area("Resume Content", st.session_state.resume_data['full_text'], height=200)
            else:
                st.error("❌ Could not extract text from the uploaded file.")
    
    elif page == " Generate Questions":
        st.markdown('<div class="section-header">Generate Interview Questions</div>', unsafe_allow_html=True)
        
        if st.session_state.resume_data is None:
            st.warning(" Please upload your resume first!")
            return
        
        # Question generation settings
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.slider("Number of questions", 3, 10, 5)
        with col2:
            question_type = st.selectbox(
                "Focus area",
                ["Mixed", "Technical", "Behavioral", "Experience-based"]
            )
        
        if st.button(" Generate Questions", type="primary"):
            with st.spinner("Generating personalized questions..."):
                st.session_state.questions = question_generator.generate_questions(
                    st.session_state.resume_data, 
                    num_questions
                )
            st.success(f"✅ Generated {len(st.session_state.questions)} questions!")
        
        # Display generated questions
        if st.session_state.questions:
            st.subheader(" Generated Interview Questions")
            for i, question in enumerate(st.session_state.questions, 1):
                st.markdown(f'<div class="question-box"><strong>Q{i}:</strong> {question}</div>', 
                           unsafe_allow_html=True)
    
    elif page == " Answer Questions":
        st.markdown('<div class="section-header">Answer Interview Questions</div>', unsafe_allow_html=True)
        
        if not st.session_state.questions:
            st.warning(" Please generate questions first!")
            return
        
        # Answer input interface
        st.subheader(" Provide Your Answers")
        
        for i, question in enumerate(st.session_state.questions):
            st.markdown(f'<div class="question-box"><strong>Question {i+1}:</strong><br>{question}</div>', 
                       unsafe_allow_html=True)
            
            # Answer input
            answer_key = f"answer_{i}"
            widget_key   = f"text_{answer_key}"
            typed_text = st.text_area(
            f"✍️  Type your answer to Question {i+1}:",
            value=st.session_state.answers.get(answer_key, ""),
            height=100,
            key=answer_key,
            placeholder="Type your answer here or use the mic below…"
                )
            st.session_state.answers[answer_key] = typed_text.strip()

            if st.button(f"🎙️  Record Answer {i+1}", key=f"rec_{i}"):
                spoken = st.session_state.speech_rec.record(timeout=8, phrase_time_limit=60)
                if spoken:
                    # store in answers dict AND update textarea value
                    st.session_state.answers[answer_key] = spoken.strip()
                    st.success(f"✅ Transcribed Answer:\n\n{spoken.strip()}")

            current_answer = st.session_state.answers.get(answer_key, "").strip()

            if current_answer:
                if st.button(f" Evaluate Answer {i+1}", key=f"eval_{i}"):
                    with st.spinner("Evaluating your answer…"):
                        evaluation = evaluator.evaluate_answer(question, current_answer)
                        st.session_state.evaluations[answer_key] = evaluation

                if answer_key in st.session_state.evaluations:
                    eval_data = st.session_state.evaluations[answer_key]
                    score_cols = st.columns(5)
                    for j, (category, data) in enumerate(eval_data.items()):
                        with score_cols[j]:
                            color = (
                                "green" if data["score"] >= 7
                                else "orange" if data["score"] >= 5
                                else "red"
                            )

                            st.markdown(
                                f"""
                                <div class="score-card" style="border-left-color: {color};">
                                    <h4>{category.title()}</h4>
                                    <h2 style="color: {color};">{data['score']}/10</h2>
                                    <small>{data['top_label']}</small>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
            st.markdown("---")
    
    elif page == " View Results":
        st.markdown('<div class="section-header">Interview Results & Analysis</div>', unsafe_allow_html=True)
        
        if not st.session_state.evaluations:
            st.warning("⚠️ Please answer and evaluate questions first!")
            return
        
        # Overall performance summary
        all_scores = {}
        categories = ['confidence', 'clarity', 'positivity', 'relevance', 'professionalism']
        
        # Debug: Show structure of evaluations
        if st.checkbox(" Debug Mode - Show Data Structure"):
            st.write("**Evaluation Data Structure:**")
            st.json(dict(list(st.session_state.evaluations.items())[:1]))  # Show first item
        
        for category in categories:
            scores = []
            for eval_key, eval_data in st.session_state.evaluations.items():
                if isinstance(eval_data, dict) and category in eval_data:
                    if isinstance(eval_data[category], dict) and 'score' in eval_data[category]:
                        scores.append(eval_data[category]['score'])
                    elif isinstance(eval_data[category], (int, float)):
                        scores.append(eval_data[category])
            
            if scores:
                all_scores[category] = {
                    'average': sum(scores) / len(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'count': len(scores)
                }
        
        # Overall score calculation
        if all_scores:
            overall_score = sum(scores['average'] for scores in all_scores.values()) / len(all_scores)
        else:
            overall_score = 0
            st.error("⚠️ No valid evaluation data found. Please ensure answers are properly evaluated.")
            return
        
        # Display overall performance
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Score", f"{overall_score:.1f}/10")
        with col2:
            performance_level = "Excellent" if overall_score >= 8 else "Good" if overall_score >= 6 else "Average" if overall_score >= 4 else "Needs Improvement"
            st.metric("Performance Level", performance_level)
        with col3:
            total_questions = len(st.session_state.evaluations)
            st.metric("Questions Answered", total_questions)
        
        # Radar chart visualization
        if all_scores:
            try:
                fig = create_score_visualization(all_scores)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating visualization: {e}")
                
                # Fallback: Simple bar chart
                st.subheader(" Performance Scores")
                chart_data = pd.DataFrame([
                    {'Category': cat.title(), 'Score': data['average']} 
                    for cat, data in all_scores.items()
                ])
                st.bar_chart(chart_data.set_index('Category'))
        else:
            st.warning("No evaluation data available for visualization.")
        
        # Detailed breakdown
        st.subheader(" Detailed Performance Breakdown")
        
        performance_df = pd.DataFrame([
            {
                'Category': category.title(),
                'Average Score': f"{data['average']:.1f}",
                'Range': f"{data['min']:.1f} - {data['max']:.1f}",
                'Status': '🟢 Strong' if data['average'] >= 7 else '🟡 Good' if data['average'] >= 5 else '🔴 Needs Work'
            }
            for category, data in all_scores.items()
        ])
        
        st.dataframe(performance_df, use_container_width=True)
        
        # Recommendations
        st.subheader(" Recommendations for Improvement")
        
        weak_areas = [cat for cat, data in all_scores.items() if data['average'] < 6]
        strong_areas = [cat for cat, data in all_scores.items() if data['average'] >= 7]
        
        if weak_areas:
            st.warning("**Areas for Improvement:**")
            for area in weak_areas:
                recommendations = {
                    'confidence': "Practice speaking with more conviction. Avoid hedge words like 'maybe' or 'I think'.",
                    'clarity': "Structure your answers better. Use the STAR method (Situation, Task, Action, Result).",
                    'positivity': "Show more enthusiasm about the role and company. Use positive language.",
                    'relevance': "Stay focused on the question. Provide specific examples related to the topic.",
                    'professionalism': "Use formal language and maintain professional tone throughout."
                }
                st.write(f"• **{area.title()}**: {recommendations.get(area, 'Focus on improving this area.')}")
        
        if strong_areas:
            st.success("**Your Strengths:**")
            for area in strong_areas:
                st.write(f"• **{area.title()}**: You performed well in this area!")
        
        # Export results
        if st.button("📥 Download Results Report"):
            # Create downloadable report
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'overall_score': overall_score,
                'performance_breakdown': all_scores,
                'questions_and_answers': [
                    {
                        'question': st.session_state.questions[i],
                        'answer': st.session_state.answers.get(f'answer_{i}', ''),
                        'evaluation': st.session_state.evaluations.get(f'answer_{i}', {})
                    }
                    for i in range(len(st.session_state.questions))
                ]
            }
            
            report_json = json.dumps(report_data, indent=2)
            st.download_button(
                label="Download JSON Report",
                data=report_json,
                file_name=f"interview_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p> AI Interview Evaluator | Built with Streamlit & Transformers</p>
        <p> Tip: For best results, provide detailed answers with specific examples</p>
    </div>
    """, 
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main()