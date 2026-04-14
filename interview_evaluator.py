# import re
# import streamlit as st
# from transformers import pipeline
# from datetime import datetime

# class InterviewEvaluator:
#     """Evaluate interview answers using transformer models"""

#     def __init__(self):
#         try:
#             self.classifier = pipeline(
#                 "zero-shot-classification",
#                 model="facebook/bart-large-mnli"
#             )
#             self.model_loaded = True
#         except Exception as e:
#             st.error(f"Error loading evaluation model: {e}")
#             self.model_loaded = False

#     def evaluate_answer(self, question, answer):
#         """Evaluate a single answer across multiple soft skill dimensions."""
#         if not self.model_loaded:
#             return self.fallback_evaluation(answer)

#         try:
#             categories = {
#                 'confidence': ['confident', 'self-assured', 'certain', 'decisive'],
#                 'clarity': ['clear', 'well-structured', 'coherent', 'articulate'],
#                 'positivity': ['positive attitude', 'enthusiastic tone', 'hopeful language', 'motivated response', 'friendly tone'],
#                 'relevance': ['relevant', 'on-topic', 'appropriate', 'related'],
#                 'professionalism': ['professional', 'appropriate', 'respectful', 'formal']
#             }

#             results = {}
#             for category, labels in categories.items():
#                 template = "The answer reflects {}." if category == 'positivity' else "The answer is {}."
#                 result = self.classifier(
#                     answer,
#                     candidate_labels=labels,
#                     hypothesis_template=template
#                 )

#                 top_score = result['scores'][0]
#                 avg_top3 = sum(result['scores'][:3]) / 3
#                 score = ((top_score * 0.7) + (avg_top3 * 0.3)) * 12
#                 score = min(score, 10.0)

#                 results[category] = {
#                     'score': round(score, 1),
#                     'confidence': round(top_score, 3),
#                     'top_label': result['labels'][0]
#                 }

#             return results

#         except Exception as e:
#             st.error(f"Error in evaluation: {e}")
#             return self.fallback_evaluation(answer)

#     def fallback_evaluation(self, answer):
#         """Heuristic fallback if model fails."""
#         word_count = len(answer.split())
#         sentence_count = len(re.split(r'[.!?]+', answer))
#         avg_sentence_length = word_count / max(sentence_count, 1)

#         confidence_score = min(10, max(1, 5 + (word_count > 20) * 2 + (avg_sentence_length > 10) * 2))
#         clarity_score = min(10, max(1, 5 + (sentence_count > 2) * 2 + (word_count > 30) * 1))
#         positivity_score = 6
#         relevance_score = min(10, max(1, 4 + (word_count > 15) * 3))
#         professionalism_score = 7

#         return {
#             'confidence': {'score': confidence_score, 'confidence': 0.8, 'top_label': 'confident'},
#             'clarity': {'score': clarity_score, 'confidence': 0.8, 'top_label': 'clear'},
#             'positivity': {'score': positivity_score, 'confidence': 0.8, 'top_label': 'neutral'},
#             'relevance': {'score': relevance_score, 'confidence': 0.8, 'top_label': 'relevant'},
#             'professionalism': {'score': professionalism_score, 'confidence': 0.8, 'top_label': 'professional'}
#         }

# class QuestionGenerator:
#     """Generate interview questions using a T5 model based on resume content."""

#     def __init__(self):
#         try:
#             self.generator = pipeline(
#                 "text2text-generation",
#                 model="google/flan-t5-base"
#             )
#         except Exception as e:
#             st.warning("Failed to load question generation model. Using fallback.")
#             self.generator = None

#     def generate_questions(self, resume_text, num_questions=5):
#         """Generate relevant interview questions from resume text."""
#         questions = []

#         if self.generator:
#             prompt = f"Generate {num_questions} interview questions based on the following resume:\n{resume_text}"
#             output = self.generator(prompt, max_length=512, do_sample=True, num_return_sequences=1)[0]['generated_text']
#             questions = [q.strip() for q in re.split(r'\n|\?|\.', output) if len(q.strip()) > 10][:num_questions]
#         else:
#             questions = [
#                 "Tell me about your background.",
#                 "Describe a challenge you've faced at work.",
#                 "What are your strengths?",
#                 "Where do you see yourself in five years?",
#                 "How do you handle tight deadlines?"
#             ]

#         return questions




import openai
import os
import streamlit as st

class InterviewEvaluator:
    """Evaluate interview answers using OpenAI Chat API"""

    def __init__(self, api_key):
        openai.api_key = api_key
        self.model = "gpt-3.5-turbo"  # or "gpt-4" if available

    def evaluate_answer(self, question, answer):
        try:
            system_prompt = (
                "You are an AI assistant trained to evaluate interview answers. "
                "Given a candidate's response, you must score them on the following 5 categories:\n"
                "- Confidence (out of 10)\n"
                "- Clarity (out of 10)\n"
                "- Positivity (out of 10)\n"
                "- Relevance (out of 10)\n"
                "- Professionalism (out of 10)\n\n"
                "Return a JSON dictionary like:\n"
                "{ 'confidence': 8.5, 'clarity': 7.0, 'positivity': 6.5, 'relevance': 9.0, 'professionalism': 8.0 }"
            )

            user_input = (
                f"Question: {question}\n"
                f"Answer: {answer}\n"
                "Evaluate this answer based on the above categories."
            )

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.4
            )

            # Parse response
            raw_text = response.choices[0].message.content.strip()
            scores = eval(raw_text) if raw_text.startswith("{") else {}
            
            # Convert to consistent format
            return {
                k: {'score': round(float(v), 1), 'confidence': 0.9, 'top_label': k}
                for k, v in scores.items()
            }

        except Exception as e:
            st.error(f"Error using ChatGPT for evaluation: {e}")
            return self.fallback_evaluation(answer)

    def fallback_evaluation(self, answer):
        """Fallback if API fails"""
        word_count = len(answer.split())
        return {
            'confidence': {'score': 6.0, 'confidence': 0.8, 'top_label': 'confident'},
            'clarity': {'score': 5.5, 'confidence': 0.8, 'top_label': 'clear'},
            'positivity': {'score': 6.0, 'confidence': 0.8, 'top_label': 'positive'},
            'relevance': {'score': 7.0, 'confidence': 0.8, 'top_label': 'relevant'},
            'professionalism': {'score': 7.5, 'confidence': 0.8, 'top_label': 'professional'}
        }

