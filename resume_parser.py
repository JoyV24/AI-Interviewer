import re
import docx
import PyPDF2
import streamlit as st
from datetime import datetime
from dateutil import parser

class ResumeParser:
    """Extract text and key information from resume files"""

    @staticmethod
    def extract_text_from_pdf(pdf_file):
        """Extract text from PDF resume"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(docx_file):
        """Extract text from DOCX resume"""
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {e}")
            return ""

    @staticmethod
    def safe_parse_date(date_str):
        try:
            return parser.parse(date_str, default=datetime(2000, 1, 1))
        except:
            return None

    @staticmethod
    def parse_resume_content(text):
        """Extract key information from resume text"""
        skills = []
        experience_years = 0
        education = []

        # ---------- Extract Skills ----------
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'machine learning', 'data science',
            'tensorflow', 'pytorch', 'git', 'agile', 'scrum', 'c++', 'c#',
            'ruby', 'php', 'html', 'css', 'angular', 'vue.js', 'django', 'flask',
            'spring', 'api', 'restful services', 'microservices', 'linux', 'unix',
            'devops', 'ci/cd', 'jenkins', 'ansible', 'terraform', 'azure', 'gcp',
            'big data', 'hadoop', 'spark', 'kafka', 'data analysis', 'data visualization',
            'tableau', 'power bi', 'natural language processing', 'nlp', 'computer vision',
        ]

        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.title())

        skills = list(set(skills))  # remove duplicates

        # ---------- Extract Experience Duration ----------
        date_range_patterns = [
            r'(\d{2}/\d{2}/\d{4})\s*[–-]\s*(\d{2}/\d{2}/\d{4}|Present)',
            r'(\d{1,2}/\d{4})\s*[–-]\s*(\d{1,2}/\d{4}|Present)',
            r'([A-Za-z]+\s\d{4})\s*[–-]\s*([A-Za-z]+\s\d{4}|Present)',
            r'(\d{4})\s*[–-]\s*(\d{4}|Present)',
        ]

        total_months = 0
        for pattern in date_range_patterns:
            matches = re.findall(pattern, text)
            for start_str, end_str in matches:
                try:
                    start_date = ResumeParser.safe_parse_date(start_str)
                    end_date = datetime.today() if end_str.lower() == "present" else ResumeParser.safe_parse_date(end_str)
                    if start_date and end_date:
                        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                        total_months += max(months, 0)
                except:
                    continue

        experience_years = round(total_months / 12, 1)

        # ---------- Extract Education ----------
        education_keywords = [
            'bachelor', 'b.s.', 'bsc', 'b.sc.', 'master', 'm.s.', 'msc', 'm.sc.', 'meng', 'm.eng',
            'phd', 'ph.d.', 'doctorate', 'degree', 'university', 'college', 'institute',
            'b.tech', 'm.tech', 'mba', 'm.b.a.'
        ]
        for keyword in education_keywords:
            if keyword in text_lower:
                education.append(keyword.title())

        return {
            'skills': skills[:10],  
            'experience_years': experience_years,
            'education': list(set(education)),
            'full_text': text
        }
