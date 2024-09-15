"""
Shared OpenAI API utilities for AI automation projects
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

class OpenAIClient:
    def __init__(self):
        """Initialize OpenAI client with API key"""
        # Try to get API key from environment or Streamlit secrets
        self.api_key = None
        
        if 'OPENAI_API_KEY' in os.environ:
            self.api_key = os.environ['OPENAI_API_KEY']
        elif hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            self.api_key = st.secrets['OPENAI_API_KEY']
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or in Streamlit secrets.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_completion(self, prompt, model="gpt-3.5-turbo", max_tokens=1500, temperature=0.7):
        """Generate text completion using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def generate_structured_completion(self, system_prompt, user_prompt, model="gpt-3.5-turbo", max_tokens=1500, temperature=0.7):
        """Generate structured completion with system and user prompts"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        client = OpenAIClient()
        test_response = client.generate_completion("Say 'Hello, AI automation!' in a professional tone.", max_tokens=50)
        return True, test_response
    except Exception as e:
        return False, str(e)

# Prompt templates for different use cases
RESUME_OPTIMIZATION_PROMPTS = {
    "analyze": """
    Analyze the following resume and provide detailed feedback on:
    1. Content gaps and missing keywords
    2. Structure and formatting improvements
    3. ATS (Applicant Tracking System) compatibility
    4. Industry-specific optimizations
    5. Impact statement improvements
    
    Resume Content:
    {resume_content}
    
    Target Job Description (if provided):
    {job_description}
    """,
    
    "optimize": """
    Rewrite and optimize the following resume section to be more impactful, ATS-friendly, and aligned with the target role:
    
    Original Content:
    {original_content}
    
    Target Role: {target_role}
    Key Requirements: {key_requirements}
    
    Please provide an improved version that:
    - Uses strong action verbs and quantified achievements
    - Includes relevant keywords
    - Is concise yet comprehensive
    - Follows best practices for ATS systems
    """
}

LINKEDIN_GENERATION_PROMPTS = {
    "professional_post": """
    Create an engaging LinkedIn post about {topic} that:
    1. Starts with a compelling hook
    2. Provides valuable insights or tips
    3. Includes a call-to-action
    4. Uses appropriate hashtags
    5. Is professional yet personable
    
    Target audience: {target_audience}
    Tone: {tone}
    Length: {length} (short/medium/long)
    
    Additional context: {context}
    """,
    
    "industry_insights": """
    Write a LinkedIn post sharing insights about {industry_topic}:
    
    Key points to cover:
    {key_points}
    
    Make it:
    - Thought-provoking and engaging
    - Include personal perspective or experience
    - Add 2-3 relevant questions to encourage engagement
    - Use 5-8 relevant hashtags
    - Professional but conversational tone
    """
}

EMAIL_RESPONSE_PROMPTS = {
    "professional_reply": """
    Generate a professional email response based on the following:
    
    Original Email:
    {original_email}
    
    Response Context:
    {response_context}
    
    Tone: {tone} (formal/semi-formal/friendly)
    
    Please create a response that:
    - Addresses all points from the original email
    - Is appropriately professional
    - Includes proper email etiquette
    - Is concise yet complete
    """,
    
    "customer_service": """
    Create a customer service email response for:
    
    Customer Query: {customer_query}
    Issue Type: {issue_type}
    Resolution: {resolution}
    
    The response should be:
    - Empathetic and understanding
    - Clear about next steps
    - Professional yet warm
    - Include contact information for follow-up
    """
}
