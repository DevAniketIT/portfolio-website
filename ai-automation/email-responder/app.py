"""
AI-Powered Email Responder
Generates professional email responses using OpenAI GPT
"""

import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import re
from email_validator import validate_email, EmailNotValidError

# Add parent directory to path to import shared utilities
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from shared_utils.openai_utils import OpenAIClient, EMAIL_RESPONSE_PROMPTS

class EmailResponder:
    def __init__(self):
        """Initialize the Email Responder"""
        self.openai_client = None
        
    def initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            self.openai_client = OpenAIClient()
            return True, "OpenAI client initialized successfully!"
        except Exception as e:
            return False, f"Failed to initialize OpenAI client: {str(e)}"
    
    def extract_email_details(self, email_content):
        """Extract key details from email content"""
        details = {
            'subject': '',
            'sender': '',
            'key_points': [],
            'questions': [],
            'action_items': []
        }
        
        # Simple extraction logic - can be enhanced
        lines = email_content.split('\n')
        
        # Look for subject line
        subject_pattern = r'^Subject:\s*(.+)'
        for line in lines:
            subject_match = re.match(subject_pattern, line, re.IGNORECASE)
            if subject_match:
                details['subject'] = subject_match.group(1)
                break
        
        # Look for sender
        sender_pattern = r'^From:\s*(.+)'
        for line in lines:
            sender_match = re.match(sender_pattern, line, re.IGNORECASE)
            if sender_match:
                details['sender'] = sender_match.group(1)
                break
        
        # Look for questions (lines ending with ?)
        for line in lines:
            if line.strip().endswith('?'):
                details['questions'].append(line.strip())
        
        return details
    
    def generate_professional_reply(self, original_email, response_context, tone):
        """Generate professional email response"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = EMAIL_RESPONSE_PROMPTS["professional_reply"].format(
            original_email=original_email,
            response_context=response_context,
            tone=tone
        )
        
        return self.openai_client.generate_completion(prompt, max_tokens=1000, temperature=0.6)
    
    def generate_customer_service_reply(self, customer_query, issue_type, resolution):
        """Generate customer service response"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = EMAIL_RESPONSE_PROMPTS["customer_service"].format(
            customer_query=customer_query,
            issue_type=issue_type,
            resolution=resolution
        )
        
        return self.openai_client.generate_completion(prompt, max_tokens=800, temperature=0.6)
    
    def generate_followup_email(self, context, purpose):
        """Generate follow-up emails"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompts = {
            "Meeting Follow-up": f"""
            Write a professional follow-up email after a meeting:
            
            Context: {context}
            
            Include:
            - Thank the participants
            - Summarize key decisions made
            - List action items with owners
            - Mention next steps
            - Professional closing
            """,
            
            "Sales Follow-up": f"""
            Write a sales follow-up email:
            
            Context: {context}
            
            Include:
            - Reference to previous conversation
            - Address any concerns mentioned
            - Provide additional value/information
            - Clear call-to-action
            - Professional yet persuasive tone
            """,
            
            "Application Follow-up": f"""
            Write a professional job application follow-up email:
            
            Context: {context}
            
            Include:
            - Reference to applied position
            - Reaffirm interest and qualifications
            - Add any new relevant information
            - Professional and respectful tone
            - Request for status update
            """,
            
            "General Follow-up": f"""
            Write a professional follow-up email:
            
            Context: {context}
            
            Include:
            - Reference to previous communication
            - Purpose of follow-up
            - Next steps or questions
            - Professional closing
            """
        }
        
        prompt = prompts.get(purpose, prompts["General Follow-up"])
        return self.openai_client.generate_completion(prompt, max_tokens=600, temperature=0.6)
    
    def generate_email_templates(self, template_type, industry):
        """Generate email templates for different purposes"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = f"""
        Create a professional email template for {template_type} in the {industry} industry.
        
        The template should:
        - Be professional and industry-appropriate
        - Include placeholders for customization (e.g., [NAME], [COMPANY])
        - Have proper email structure (subject, greeting, body, closing)
        - Be adaptable for different situations
        
        Template Type: {template_type}
        Industry: {industry}
        """
        
        return self.openai_client.generate_completion(prompt, max_tokens=600, temperature=0.5)

def save_email_to_history(email_content, email_type, context):
    """Save generated email to history"""
    if 'email_history' not in st.session_state:
        st.session_state.email_history = []
    
    email_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': email_type,
        'context': context[:50] + "..." if len(context) > 50 else context,
        'content': email_content[:100] + "..." if len(email_content) > 100 else email_content
    }
    
    st.session_state.email_history.insert(0, email_data)
    # Keep only last 15 emails
    st.session_state.email_history = st.session_state.email_history[:15]

def main():
    st.set_page_config(
        page_title="AI Email Responder",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("📧 AI-Powered Email Responder")
    st.markdown("""
    Generate professional email responses, follow-ups, and templates using AI.
    Perfect for businesses, professionals, and customer service teams looking to maintain 
    consistent, professional email communication.
    """)
    
    # Initialize the responder
    if 'responder' not in st.session_state:
        st.session_state.responder = EmailResponder()
    
    # Sidebar for API configuration and settings
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password",
                               help="Enter your OpenAI API key to use AI features")
        
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            if st.button("Initialize AI"):
                success, message = st.session_state.responder.initialize_openai()
                if success:
                    st.success(message)
                    st.session_state.ai_initialized = True
                else:
                    st.error(message)
                    st.session_state.ai_initialized = False
        
        # Service information
        st.markdown("---")
        st.header("💼 Service Pricing")
        st.markdown("""
        **Fiverr Services:**
        - Email Response Setup: ₹2,500
        - Custom Templates (10): ₹3,000
        - Email Automation System: ₹5,000
        - Training & Setup: ₹4,000
        
        **Business Packages:**
        - Small Business (50 emails/month): ₹3,500
        - Enterprise (Unlimited): ₹8,000
        """)
        
        # Email history
        st.markdown("---")
        st.header("📧 Recent Emails")
        if hasattr(st.session_state, 'email_history') and st.session_state.email_history:
            for i, email in enumerate(st.session_state.email_history[:5]):
                with st.expander(f"{email['type']} - {email['timestamp']}"):
                    st.write(f"**Context:** {email['context']}")
                    st.write(email['content'])
        else:
            st.info("No emails generated yet")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Reply Generator", "📬 Follow-up Emails", "📋 Templates", "🤖 Bulk Processing"])
    
    with tab1:
        st.header("Generate Email Response")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Original email input
            st.subheader("📨 Original Email")
            original_email = st.text_area(
                "Paste the email you need to respond to:",
                height=200,
                placeholder="""From: john@company.com
Subject: Project Update Required

Hi,

I hope you're doing well. I wanted to follow up on the project we discussed last week. Could you please provide an update on the current status?

Also, do you have an estimated completion date?

Best regards,
John Smith"""
            )
            
            # Response context
            st.subheader("📝 Response Details")
            response_context = st.text_area(
                "What do you want to communicate in your response?",
                height=100,
                placeholder="e.g., Project is on track, completion by Friday, will send detailed report..."
            )
            
            # Email type selection
            email_type = st.radio(
                "Email Type:",
                ["Professional Reply", "Customer Service", "Sales Response", "Internal Communication"]
            )
        
        with col2:
            st.subheader("⚙️ Settings")
            
            tone = st.selectbox(
                "Response Tone",
                ["Formal", "Semi-formal", "Friendly", "Professional", "Apologetic"]
            )
            
            include_elements = st.multiselect(
                "Include in Response:",
                ["Thank you note", "Acknowledgment", "Next steps", "Contact information", "Signature line"],
                default=["Thank you note", "Next steps"]
            )
            
            priority = st.selectbox("Priority Level", ["Low", "Normal", "High", "Urgent"])
            
            # Quick actions
            st.markdown("---")
            st.subheader("🚀 Quick Actions")
            
            if st.button("📊 Analyze Email", use_container_width=True):
                if original_email:
                    details = st.session_state.responder.extract_email_details(original_email)
                    st.json(details)
                else:
                    st.warning("Please paste an email first!")
        
        # Generate response button
        if st.button("🤖 Generate Response", type="primary", use_container_width=True):
            if not getattr(st.session_state, 'ai_initialized', False):
                st.error("Please configure your OpenAI API key first!")
            elif not original_email:
                st.error("Please paste the original email!")
            elif not response_context:
                st.error("Please provide response context!")
            else:
                try:
                    with st.spinner("AI is crafting your email response..."):
                        if email_type == "Customer Service":
                            # For customer service, extract issue type
                            issue_type = "General inquiry"  # Could be enhanced with classification
                            response = st.session_state.responder.generate_customer_service_reply(
                                original_email, issue_type, response_context
                            )
                        else:
                            response = st.session_state.responder.generate_professional_reply(
                                original_email, response_context, tone.lower()
                            )
                        
                        # Display result
                        st.markdown("---")
                        st.subheader("📧 Generated Email Response")
                        
                        # Email preview
                        st.text_area("Your Email Response:", response, height=300, key="generated_email")
                        
                        # Action buttons
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            st.download_button(
                                "📥 Download",
                                response,
                                f"email_response_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                            )
                        with col_btn2:
                            if st.button("💾 Save to History"):
                                save_email_to_history(response, email_type, response_context)
                                st.success("Email saved to history!")
                        with col_btn3:
                            if st.button("📋 Copy Format"):
                                st.code(response)
                                st.info("Copy the formatted text above!")
                
                except Exception as e:
                    st.error(f"Error generating email: {str(e)}")
    
    with tab2:
        st.header("Follow-up Email Generator")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Follow-up type
            followup_type = st.selectbox(
                "Follow-up Type",
                ["Meeting Follow-up", "Sales Follow-up", "Application Follow-up", "General Follow-up"]
            )
            
            # Context input
            followup_context = st.text_area(
                "Context/Background:",
                height=150,
                placeholder="""e.g., 
- Meeting held on Monday about Q1 budget
- Discussed marketing campaign strategies
- John to provide cost estimates by Wednesday
- Next meeting scheduled for Friday"""
            )
            
            # Additional settings
            recipient_name = st.text_input("Recipient Name (Optional)", placeholder="John Smith")
            subject_suggestion = st.checkbox("Generate Subject Line", value=True)
        
        with col2:
            st.subheader("📅 Follow-up Settings")
            
            urgency = st.select_slider(
                "Urgency Level",
                options=["Low", "Medium", "High", "Urgent"],
                value="Medium"
            )
            
            include_deadline = st.checkbox("Include Deadline/Timeline")
            if include_deadline:
                deadline = st.date_input("Deadline Date")
            
            followup_tone = st.selectbox(
                "Email Tone",
                ["Professional", "Friendly", "Formal", "Casual"]
            )
            
            # Templates preview
            st.markdown("---")
            st.subheader("📋 Template Examples")
            
            templates = {
                "Meeting Follow-up": "Thank + Summary + Action Items + Next Steps",
                "Sales Follow-up": "Reference + Value + Objection Handling + CTA",
                "Application Follow-up": "Reference + Interest + Qualification + Status Request",
                "General Follow-up": "Context + Purpose + Questions + Next Steps"
            }
            
            st.info(templates.get(followup_type, "General structure"))
        
        # Generate follow-up button
        if st.button("📬 Generate Follow-up", type="primary", use_container_width=True):
            if not getattr(st.session_state, 'ai_initialized', False):
                st.error("Please configure your OpenAI API key first!")
            elif not followup_context:
                st.error("Please provide context for the follow-up!")
            else:
                try:
                    with st.spinner("Creating your follow-up email..."):
                        enhanced_context = followup_context
                        if recipient_name:
                            enhanced_context += f"\nRecipient: {recipient_name}"
                        if include_deadline and 'deadline' in locals():
                            enhanced_context += f"\nDeadline: {deadline}"
                        
                        followup_email = st.session_state.responder.generate_followup_email(
                            enhanced_context, followup_type
                        )
                        
                        # Display result
                        st.markdown("---")
                        st.subheader("📬 Generated Follow-up Email")
                        
                        st.text_area("Follow-up Email:", followup_email, height=300, key="followup_email")
                        
                        # Generate subject line if requested
                        if subject_suggestion:
                            with st.spinner("Generating subject line..."):
                                subject_prompt = f"Generate a professional email subject line for this {followup_type.lower()}: {followup_context[:100]}..."
                                subject_line = st.session_state.responder.openai_client.generate_completion(
                                    subject_prompt, max_tokens=50, temperature=0.5
                                )
                                st.info(f"📋 Suggested Subject: {subject_line}")
                        
                        # Download button
                        st.download_button(
                            "📥 Download Follow-up Email",
                            followup_email,
                            f"followup_{followup_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
                        )
                
                except Exception as e:
                    st.error(f"Error generating follow-up: {str(e)}")
    
    with tab3:
        st.header("Email Templates Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Template type selection
            template_type = st.selectbox(
                "Template Type",
                [
                    "Welcome Email", "Thank You Email", "Appointment Confirmation",
                    "Payment Reminder", "Newsletter", "Product Launch",
                    "Customer Support", "Meeting Invitation", "Proposal Follow-up",
                    "Contract Renewal", "Event Invitation", "Survey Request"
                ]
            )
            
            # Industry selection
            industry = st.selectbox(
                "Industry/Business Type",
                [
                    "Technology", "Healthcare", "Finance", "Education", "Retail",
                    "Real Estate", "Marketing", "Legal", "Consulting", "Manufacturing",
                    "Non-profit", "Government", "General Business"
                ]
            )
        
        with col2:
            # Template settings
            st.subheader("🎨 Template Settings")
            
            template_style = st.selectbox(
                "Style",
                ["Professional", "Friendly", "Formal", "Modern", "Traditional"]
            )
            
            include_placeholders = st.checkbox("Include Placeholders", value=True)
            include_signature = st.checkbox("Include Signature Block", value=True)
            
            # Template features
            st.markdown("**Template Features:**")
            features = st.multiselect(
                "Include:",
                ["Header/Logo area", "Call-to-action buttons", "Contact information", 
                 "Social media links", "Unsubscribe link", "Legal disclaimer"],
                default=["Call-to-action buttons", "Contact information"]
            )
        
        # Generate template button
        if st.button("📋 Generate Template", type="primary", use_container_width=True):
            if not getattr(st.session_state, 'ai_initialized', False):
                st.error("Please configure your OpenAI API key first!")
            else:
                try:
                    with st.spinner("Creating email template..."):
                        template = st.session_state.responder.generate_email_templates(
                            template_type, industry
                        )
                        
                        # Display result
                        st.markdown("---")
                        st.subheader(f"📋 {template_type} Template")
                        
                        st.text_area("Email Template:", template, height=400, key="email_template")
                        
                        # Template info
                        st.info(f"""
                        **Template Details:**
                        - Type: {template_type}
                        - Industry: {industry}
                        - Style: {template_style}
                        - Placeholders: {'Included' if include_placeholders else 'Not included'}
                        """)
                        
                        # Download and save options
                        col_temp1, col_temp2, col_temp3 = st.columns(3)
                        with col_temp1:
                            st.download_button(
                                "📥 Download Template",
                                template,
                                f"{template_type.lower().replace(' ', '_')}_template.txt"
                            )
                        with col_temp2:
                            if st.button("💾 Save Template"):
                                save_email_to_history(template, f"{template_type} Template", industry)
                                st.success("Template saved!")
                        with col_temp3:
                            if st.button("🔄 Generate Variation"):
                                st.rerun()
                
                except Exception as e:
                    st.error(f"Error generating template: {str(e)}")
        
        # Template library
        st.markdown("---")
        st.subheader("📚 Template Examples")
        
        example_templates = {
            "Welcome Email": "Perfect for onboarding new customers or team members",
            "Thank You Email": "Show appreciation after purchases, meetings, or collaborations",
            "Appointment Confirmation": "Confirm scheduled meetings or consultations",
            "Payment Reminder": "Professional reminders for overdue invoices",
            "Product Launch": "Announce new products or services to your audience"
        }
        
        for template, description in example_templates.items():
            st.write(f"**{template}:** {description}")
    
    with tab4:
        st.header("Bulk Email Processing")
        
        st.info("Process multiple emails at once - perfect for customer service teams!")
        
        # Bulk processing options
        processing_type = st.radio(
            "Processing Type:",
            ["Multiple Replies", "Template Generation", "Email Analysis"]
        )
        
        if processing_type == "Multiple Replies":
            col_bulk1, col_bulk2 = st.columns(2)
            
            with col_bulk1:
                bulk_emails = st.text_area(
                    "Emails to Process (separate with '---'):",
                    height=200,
                    placeholder="""Email 1: Customer asking about refund policy
---
Email 2: Client requesting project update
---
Email 3: Partner inquiry about collaboration"""
                )
                
                bulk_response_context = st.text_area(
                    "General Response Guidelines:",
                    height=100,
                    placeholder="Company policy is... Standard response should include..."
                )
            
            with col_bulk2:
                bulk_tone = st.selectbox("Tone for all responses", ["Professional", "Friendly", "Formal"])
                bulk_type = st.selectbox("Response type", ["Customer Service", "Professional Reply", "Sales Response"])
                
                if st.button("🔄 Process All Emails", type="primary"):
                    if not getattr(st.session_state, 'ai_initialized', False):
                        st.error("Please configure your OpenAI API key first!")
                    elif not bulk_emails.strip():
                        st.error("Please provide emails to process!")
                    else:
                        emails_list = [email.strip() for email in bulk_emails.split('---') if email.strip()]
                        
                        with st.spinner(f"Processing {len(emails_list)} emails..."):
                            responses = []
                            
                            for i, email in enumerate(emails_list):
                                try:
                                    response = st.session_state.responder.generate_professional_reply(
                                        email, bulk_response_context, bulk_tone.lower()
                                    )
                                    responses.append({
                                        'original': email,
                                        'response': response
                                    })
                                except Exception as e:
                                    st.error(f"Error processing email {i+1}: {str(e)}")
                            
                            # Display results
                            st.markdown("---")
                            st.subheader(f"📊 Processed {len(responses)} Emails")
                            
                            for i, result in enumerate(responses):
                                with st.expander(f"Email Response {i+1}"):
                                    col_orig, col_resp = st.columns(2)
                                    with col_orig:
                                        st.markdown("**Original:**")
                                        st.text_area("", result['original'], height=150, disabled=True, key=f"orig_{i}")
                                    with col_resp:
                                        st.markdown("**Response:**")
                                        st.text_area("", result['response'], height=150, key=f"resp_{i}")
                            
                            # Download all responses
                            if responses:
                                bulk_content = "\n\n" + "="*50 + "\n\n".join([
                                    f"ORIGINAL EMAIL:\n{r['original']}\n\nRESPONSE:\n{r['response']}"
                                    for r in responses
                                ])
                                
                                st.download_button(
                                    "📥 Download All Responses",
                                    bulk_content,
                                    f"bulk_email_responses_{datetime.now().strftime('%Y%m%d')}.txt"
                                )
        
        elif processing_type == "Template Generation":
            st.subheader("Bulk Template Generation")
            
            template_types = st.multiselect(
                "Template Types to Generate:",
                ["Welcome Email", "Thank You Email", "Payment Reminder", "Meeting Invitation", "Follow-up"],
                default=["Welcome Email", "Thank You Email"]
            )
            
            industries = st.multiselect(
                "Industries:",
                ["Technology", "Healthcare", "Finance", "Retail", "Consulting"],
                default=["Technology", "Healthcare"]
            )
            
            if st.button("Generate Template Pack", type="primary"):
                if not getattr(st.session_state, 'ai_initialized', False):
                    st.error("Please configure your OpenAI API key first!")
                else:
                    total_templates = len(template_types) * len(industries)
                    with st.spinner(f"Generating {total_templates} templates..."):
                        templates = []
                        
                        for template_type in template_types:
                            for industry in industries:
                                try:
                                    template = st.session_state.responder.generate_email_templates(
                                        template_type, industry
                                    )
                                    templates.append({
                                        'type': template_type,
                                        'industry': industry,
                                        'content': template
                                    })
                                except Exception as e:
                                    st.error(f"Error generating {template_type} for {industry}: {str(e)}")
                        
                        # Display results
                        st.success(f"Generated {len(templates)} templates!")
                        
                        for template in templates:
                            with st.expander(f"{template['type']} - {template['industry']}"):
                                st.text_area("", template['content'], height=200, disabled=True, 
                                           key=f"template_{template['type']}_{template['industry']}")
                        
                        # Download all templates
                        if templates:
                            all_templates = "\n\n" + "="*60 + "\n\n".join([
                                f"TEMPLATE: {t['type']} - {t['industry']}\n\n{t['content']}"
                                for t in templates
                            ])
                            
                            st.download_button(
                                "📥 Download Template Pack",
                                all_templates,
                                f"email_template_pack_{datetime.now().strftime('%Y%m%d')}.txt"
                            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>📧 Professional Email Automation | Powered by OpenAI GPT</p>
        <p>Streamline your email communication with AI-powered responses and templates</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
