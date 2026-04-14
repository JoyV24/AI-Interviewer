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

# class QuestionGenerator:
#     """Generate interview questions based on resume content"""
    
#     def __init__(self):
#         # Initialize question generation pipeline
#         try:
#             self.generator = pipeline(
#                 "text-generation",
#                 model="microsoft/DialoGPT-medium",
#                 tokenizer="microsoft/DialoGPT-medium"
#             )
#         except:
#             # Fallback to pre-defined questions if model loading fails
#             self.generator = None
#             st.warning("Using pre-defined questions as model couldn't be loaded")
    
#     def generate_questions(self, resume_data, num_questions=5):
#         """Generate interview questions based on resume"""
#         questions = []
        
#         # Pre-defined question templates based on resume content
#         templates = {
#             'general': [
#                 "Tell me about yourself and your background.",
#                 "What interests you most about this role?",
#                 "Where do you see yourself in 5 years?"
#             ],
#             'experience': [
#                 f"You have {resume_data['experience_years']} years of experience. Can you walk me through your career journey?",
#                 "Describe a challenging project you've worked on and how you overcame obstacles.",
#                 "Tell me about a time when you had to learn a new technology quickly."
#             ],
#             'skills': [
#                 f"I see you have experience with {', '.join(resume_data['skills'][:3])}. Can you elaborate on your proficiency?",
#                 "How do you stay updated with the latest technologies in your field?",
#                 "Describe a situation where you had to use your technical skills to solve a business problem."
#             ],
#             'behavioral': [
#                 "Describe a time when you worked in a team to achieve a common goal.",
#                 "How do you handle tight deadlines and pressure?",
#                 "Tell me about a mistake you made and how you learned from it."
#             ]
#         }
        
#         # Select questions from different categories
#         categories = ['general', 'experience', 'skills', 'behavioral']
#         questions_per_category = num_questions // len(categories)
        
#         for category in categories:
#             category_questions = templates[category][:questions_per_category + 1]
#             questions.extend(category_questions)
        
#         return questions[:num_questions]


# class QuestionGenerator:
#     """Generate multiple interview questions using T5 model based on resume content."""

#     def __init__(self):
#         try:
#             self.generator = pipeline(
#                 "text2text-generation",
#                 model="google/flan-t5-large"
#             )
#         except Exception as e:
#             st.warning("Failed to load question generation model. Using fallback.")
#             self.generator = None

#     def generate_questions(self, resume_text, num_questions=5):
#         """Generate multiple interview questions from resume text."""
#         questions = []

#         if self.generator:
#             for _ in range(num_questions):
#                 prompt = f"Generate an interview question based on the following resume:\n{resume_text}"
#                 output = self.generator(
#                     prompt,
#                     max_length=64,
#                     do_sample=True,
#                     temperature=0.9,
#                     top_p=0.95,
#                     num_return_sequences=1
#                 )[0]['generated_text']

#                 cleaned = output.strip().split("\n")[0].strip(". ")
#                 if cleaned and cleaned not in questions:
#                     questions.append(cleaned)
#         else:
#             questions = [
#                 "Tell me about your background.",
#                 "Describe a challenge you've faced at work.",
#                 "What are your strengths?",
#                 "Where do you see yourself in five years?",
#                 "How do you handle tight deadlines?"
#             ]

#         return questions[:num_questions]
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the API key securely
api_key = os.getenv("OPENAI_API_KEY")

import openai
import streamlit as st

class QuestionGenerator:
    """Generate high-quality interview questions using OpenAI GPT-3.5"""

    def __init__(self, api_key):
        try:
            openai.api_key = api_key
            self.model = "gpt-3.5-turbo"
            self.max_questions = 10  # Safety cap
            self.available = True
        except Exception as e:
            st.error(f"Failed to set up OpenAI GPT: {e}")
            self.available = False

    def generate_questions(self, resume_text, num_questions=5):
        """Generate `num_questions` interview questions based on resume content"""

        if not self.available:
            st.warning("Question generation model is not available.")
            return []

        num_questions = min(num_questions, self.max_questions)
        prompt = (
            f"Generate {num_questions} interview questions based on the following resume:\n\n"
            f"{resume_text}\n\n"
            "The questions should be professional, relevant to the candidate's background, "
            "and suitable for an interview setting. Output only the list of questions."
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            output_text = response.choices[0].message.content

            # Split and clean questions
            questions = [
                line.strip(" .-–:") for line in output_text.split('\n')
                if len(line.strip()) > 10
            ]
            return questions[:num_questions]

        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return []
