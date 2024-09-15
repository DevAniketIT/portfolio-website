"""
AI-Powered Resume Optimizer
Analyzes and optimizes resumes using OpenAI GPT for better job matching and ATS compatibility
"""

import streamlit as st
import sys
import os
from pathlib import Path
import PyPDF2
from docx import Document
import io

# Add parent directory to path to import shared utilities
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from shared_utils.openai_utils import OpenAIClient, RESUME_OPTIMIZATION_PROMPTS

class ResumeOptimizer:
    def __init__(self):
        """Initialize the Resume Optimizer"""
        self.openai_client = None
        
    def initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            self.openai_client = OpenAIClient()
            return True, "OpenAI client initialized successfully!"
        except Exception as e:
            return False, f"Failed to initialize OpenAI client: {str(e)}"
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file"""
        try:
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    def analyze_resume(self, resume_content, job_description=""):
        """Analyze resume using OpenAI"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = RESUME_OPTIMIZATION_PROMPTS["analyze"].format(
            resume_content=resume_content,
            job_description=job_description or "No specific job description provided"
        )
        
        return self.openai_client.generate_completion(prompt, max_tokens=2000)
    
    def optimize_resume_section(self, original_content, target_role, key_requirements):
        """Optimize specific resume section"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = RESUME_OPTIMIZATION_PROMPTS["optimize"].format(
            original_content=original_content,
            target_role=target_role,
            key_requirements=key_requirements
        )
        
        return self.openai_client.generate_completion(prompt, max_tokens=1500)
    
    def generate_keywords(self, job_description):
        """Generate relevant keywords from job description"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = f"""
        Analyze the following job description and extract the most important keywords and phrases that should be included in a resume:
        
        Job Description:
        {job_description}
        
        Please provide:
        1. Technical skills and tools mentioned
        2. Soft skills and competencies
        3. Industry-specific terms
        4. Action verbs that would be impactful
        5. Certifications or qualifications mentioned
        
        Format as a structured list with categories.
        """
        
        return self.openai_client.generate_completion(prompt, max_tokens=1000)

def main():
    st.set_page_config(
        page_title="AI Resume Optimizer",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🤖 AI-Powered Resume Optimizer")
    st.markdown("""
    Optimize your resume for better job matching and ATS (Applicant Tracking System) compatibility using AI.
    Upload your resume and get personalized recommendations to improve your chances of landing interviews.
    """)
    
    # Initialize the optimizer
    if 'optimizer' not in st.session_state:
        st.session_state.optimizer = ResumeOptimizer()
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password", 
                               help="Enter your OpenAI API key to use AI features")
        
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            if st.button("Initialize AI"):
                success, message = st.session_state.optimizer.initialize_openai()
                if success:
                    st.success(message)
                    st.session_state.ai_initialized = True
                else:
                    st.error(message)
                    st.session_state.ai_initialized = False
        
        # Service information
        st.markdown("---")
        st.header("💼 Service Info")
        st.markdown("""
        **Fiverr Service Pricing:**
        - Basic Resume Analysis: ₹2,000
        - Full Resume Optimization: ₹3,500
        - Premium Package (Resume + Cover Letter): ₹5,000
        
        **Turnaround Time:** 24-48 hours
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Resume")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        resume_text = ""
        if uploaded_file:
            try:
                if uploaded_file.type == "application/pdf":
                    resume_text = st.session_state.optimizer.extract_text_from_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    resume_text = st.session_state.optimizer.extract_text_from_docx(uploaded_file)
                else:  # txt file
                    resume_text = str(uploaded_file.read(), "utf-8")
                
                st.success("Resume uploaded successfully!")
                
                # Show preview
                with st.expander("📄 Resume Preview"):
                    st.text_area("Content:", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, 
                               height=200, disabled=True)
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        # Manual text input option
        st.markdown("**Or paste your resume text:**")
        manual_resume = st.text_area("Resume Content", height=200, 
                                   placeholder="Paste your resume content here...")
        
        if manual_resume:
            resume_text = manual_resume
    
    with col2:
        st.header("🎯 Target Job (Optional)")
        
        job_description = st.text_area(
            "Job Description",
            height=200,
            placeholder="Paste the job description you're targeting (optional but recommended for better optimization)"
        )
        
        target_role = st.text_input("Target Role/Position", placeholder="e.g., Software Developer")
        
        # Analysis options
        st.header("🔍 Analysis Options")
        analysis_type = st.radio(
            "Choose analysis type:",
            ["Full Resume Analysis", "Section Optimization", "Keyword Extraction"]
        )
    
    # Action buttons
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        analyze_btn = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)
    
    with col_btn2:
        optimize_btn = st.button("✨ Optimize Section", use_container_width=True)
    
    with col_btn3:
        keywords_btn = st.button("🏷️ Extract Keywords", use_container_width=True)
    
    # Results area
    if analyze_btn or optimize_btn or keywords_btn:
        if not getattr(st.session_state, 'ai_initialized', False):
            st.error("Please configure your OpenAI API key first!")
            return
        
        if not resume_text:
            st.error("Please upload a resume or paste resume content!")
            return
        
        st.markdown("---")
        st.header("📊 AI Analysis Results")
        
        try:
            with st.spinner("AI is analyzing your resume..."):
                if analyze_btn and analysis_type == "Full Resume Analysis":
                    result = st.session_state.optimizer.analyze_resume(resume_text, job_description)
                    
                    st.subheader("📋 Complete Resume Analysis")
                    st.markdown(result)
                    
                    # Download results
                    st.download_button(
                        label="📥 Download Analysis",
                        data=result,
                        file_name="resume_analysis.txt",
                        mime="text/plain"
                    )
                
                elif optimize_btn and analysis_type == "Section Optimization":
                    if not target_role:
                        st.error("Please specify a target role for section optimization!")
                        return
                    
                    # For demo, optimize the whole resume as one section
                    key_reqs = "Based on the job description provided" if job_description else "General best practices"
                    result = st.session_state.optimizer.optimize_resume_section(
                        resume_text[:1000],  # Limit for demo
                        target_role,
                        key_reqs
                    )
                    
                    st.subheader("✨ Optimized Content")
                    st.markdown(result)
                
                elif keywords_btn and job_description:
                    result = st.session_state.optimizer.generate_keywords(job_description)
                    
                    st.subheader("🏷️ Relevant Keywords")
                    st.markdown(result)
                
                elif keywords_btn and not job_description:
                    st.error("Please provide a job description to extract keywords!")
        
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💡 Built for Fiverr AI Automation Services | Powered by OpenAI GPT</p>
        <p>Contact for custom AI solutions and bulk processing</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
