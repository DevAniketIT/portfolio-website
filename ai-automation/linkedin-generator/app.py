"""
AI-Powered LinkedIn Post Generator
Creates engaging, professional LinkedIn content using OpenAI GPT
"""

import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

# Add parent directory to path to import shared utilities
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from shared_utils.openai_utils import OpenAIClient, LINKEDIN_GENERATION_PROMPTS

class LinkedInGenerator:
    def __init__(self):
        """Initialize the LinkedIn Generator"""
        self.openai_client = None
        
    def initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            self.openai_client = OpenAIClient()
            return True, "OpenAI client initialized successfully!"
        except Exception as e:
            return False, f"Failed to initialize OpenAI client: {str(e)}"
    
    def generate_professional_post(self, topic, target_audience, tone, length, context=""):
        """Generate a professional LinkedIn post"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = LINKEDIN_GENERATION_PROMPTS["professional_post"].format(
            topic=topic,
            target_audience=target_audience,
            tone=tone,
            length=length,
            context=context
        )
        
        return self.openai_client.generate_completion(prompt, max_tokens=800, temperature=0.8)
    
    def generate_industry_insights(self, industry_topic, key_points):
        """Generate industry insights post"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = LINKEDIN_GENERATION_PROMPTS["industry_insights"].format(
            industry_topic=industry_topic,
            key_points=key_points
        )
        
        return self.openai_client.generate_completion(prompt, max_tokens=800, temperature=0.8)
    
    def generate_engagement_post(self, post_type, topic, personal_angle=""):
        """Generate engagement-focused posts"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompts = {
            "Question": f"""
            Create a LinkedIn post that asks a thought-provoking question about {topic}.
            Make it engaging and encourage professional discussions.
            {f"Personal angle: {personal_angle}" if personal_angle else ""}
            
            The post should:
            - Start with a compelling statement or observation
            - Ask 1-2 specific questions
            - Include relevant hashtags
            - Be conversational yet professional
            """,
            
            "Tips/Advice": f"""
            Create a LinkedIn post sharing practical tips or advice about {topic}.
            {f"Personal angle: {personal_angle}" if personal_angle else ""}
            
            Format as:
            - Hook with a problem or opportunity
            - 3-5 actionable tips
            - Conclusion with a call-to-action
            - Relevant hashtags
            """,
            
            "Success Story": f"""
            Create a LinkedIn post about a success story related to {topic}.
            {f"Personal context: {personal_angle}" if personal_angle else ""}
            
            Structure:
            - Brief background/challenge
            - Actions taken
            - Results achieved
            - Lessons learned
            - Inspirational closing
            - Relevant hashtags
            """,
            
            "Industry News": f"""
            Create a LinkedIn post commenting on industry news or trends about {topic}.
            {f"Personal perspective: {personal_angle}" if personal_angle else ""}
            
            Include:
            - Brief news summary
            - Your professional opinion
            - Implications for the industry
            - Questions for engagement
            - Relevant hashtags
            """
        }
        
        prompt = prompts.get(post_type, prompts["Tips/Advice"])
        return self.openai_client.generate_completion(prompt, max_tokens=600, temperature=0.7)
    
    def optimize_post(self, original_post, optimization_goal):
        """Optimize existing LinkedIn post"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        goals = {
            "More Engagement": "Rewrite to increase likes, comments, and shares",
            "Professional Tone": "Make more professional and business-appropriate",
            "Casual Tone": "Make more conversational and relatable",
            "Add Hashtags": "Add relevant and trending hashtags",
            "Shorten": "Make more concise while keeping key message",
            "Expand": "Add more detail and context"
        }
        
        prompt = f"""
        Optimize the following LinkedIn post to {goals.get(optimization_goal, optimization_goal)}:
        
        Original Post:
        {original_post}
        
        Please provide an improved version that maintains the core message while achieving the optimization goal.
        """
        
        return self.openai_client.generate_completion(prompt, max_tokens=600, temperature=0.6)

def save_post_to_history(post_content, post_type, topic):
    """Save generated post to history"""
    if 'post_history' not in st.session_state:
        st.session_state.post_history = []
    
    post_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': post_type,
        'topic': topic,
        'content': post_content[:100] + "..." if len(post_content) > 100 else post_content
    }
    
    st.session_state.post_history.insert(0, post_data)
    # Keep only last 20 posts
    st.session_state.post_history = st.session_state.post_history[:20]

def main():
    st.set_page_config(
        page_title="LinkedIn Post Generator",
        page_icon="💼",
        layout="wide"
    )
    
    st.title("💼 AI-Powered LinkedIn Post Generator")
    st.markdown("""
    Create engaging, professional LinkedIn content that drives engagement and builds your professional brand.
    Perfect for professionals, marketers, and businesses looking to maintain an active LinkedIn presence.
    """)
    
    # Initialize the generator
    if 'generator' not in st.session_state:
        st.session_state.generator = LinkedInGenerator()
    
    # Sidebar for API configuration and settings
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password",
                               help="Enter your OpenAI API key to use AI features")
        
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            if st.button("Initialize AI"):
                success, message = st.session_state.generator.initialize_openai()
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
        - 5 LinkedIn Posts: ₹2,000
        - 10 Posts + Strategy: ₹3,500
        - Monthly Content Plan (30 posts): ₹8,000
        - Custom Brand Voice Training: ₹5,000
        
        **Add-ons:**
        - Hashtag Research: ₹500
        - Post Scheduling: ₹1,000
        """)
        
        # Post history
        st.markdown("---")
        st.header("📝 Recent Posts")
        if hasattr(st.session_state, 'post_history') and st.session_state.post_history:
            for i, post in enumerate(st.session_state.post_history[:5]):
                with st.expander(f"{post['type']} - {post['timestamp']}"):
                    st.write(f"**Topic:** {post['topic']}")
                    st.write(post['content'])
        else:
            st.info("No posts generated yet")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["✍️ Create Post", "🔄 Optimize Post", "📊 Bulk Generator", "💡 Ideas"])
    
    with tab1:
        st.header("Create New LinkedIn Post")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Post type selection
            post_type = st.selectbox(
                "Post Type",
                ["Professional Insights", "Tips & Advice", "Question/Discussion", "Success Story", "Industry News", "Personal Branding"]
            )
            
            # Topic input
            topic = st.text_input("Topic/Subject", placeholder="e.g., AI in Healthcare, Remote Work Benefits")
            
            # Additional context
            if post_type in ["Professional Insights", "Industry News"]:
                context = st.text_area("Key Points or Context", 
                                     placeholder="Add key points you want to cover...")
            else:
                context = st.text_area("Personal Context (Optional)", 
                                     placeholder="Add personal experience or angle...")
        
        with col2:
            # Post settings
            st.subheader("Post Settings")
            
            target_audience = st.selectbox(
                "Target Audience",
                ["Professionals", "Entrepreneurs", "Students", "Industry Experts", "Job Seekers", "General Business"]
            )
            
            tone = st.selectbox(
                "Tone",
                ["Professional", "Conversational", "Inspirational", "Educational", "Thought Leadership"]
            )
            
            length = st.selectbox(
                "Post Length",
                ["Short (50-100 words)", "Medium (100-200 words)", "Long (200+ words)"]
            )
            
            include_hashtags = st.checkbox("Include Hashtags", value=True)
            include_cta = st.checkbox("Include Call-to-Action", value=True)
        
        # Generate button
        if st.button("🚀 Generate Post", type="primary", use_container_width=True):
            if not getattr(st.session_state, 'ai_initialized', False):
                st.error("Please configure your OpenAI API key first!")
            elif not topic:
                st.error("Please enter a topic!")
            else:
                try:
                    with st.spinner("AI is crafting your LinkedIn post..."):
                        if post_type == "Professional Insights":
                            result = st.session_state.generator.generate_professional_post(
                                topic, target_audience, tone.lower(), length.split()[0].lower(), context
                            )
                        elif post_type in ["Tips & Advice", "Question/Discussion", "Success Story", "Industry News"]:
                            result = st.session_state.generator.generate_engagement_post(
                                post_type.split()[0] if "/" not in post_type else "Tips/Advice", 
                                topic, context
                            )
                        else:  # Personal Branding
                            result = st.session_state.generator.generate_professional_post(
                                f"Personal branding around {topic}", target_audience, tone.lower(), 
                                length.split()[0].lower(), context
                            )
                        
                        # Display result
                        st.markdown("---")
                        st.subheader("📝 Generated LinkedIn Post")
                        
                        # Post preview box
                        st.text_area("Your LinkedIn Post:", result, height=300, key="generated_post")
                        
                        # Action buttons
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            st.download_button("📥 Download", result, f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
                        with col_btn2:
                            if st.button("💾 Save to History"):
                                save_post_to_history(result, post_type, topic)
                                st.success("Post saved to history!")
                        with col_btn3:
                            if st.button("📋 Copy to Clipboard"):
                                st.code(result)
                                st.info("Copy the text from the box above!")
                
                except Exception as e:
                    st.error(f"Error generating post: {str(e)}")
    
    with tab2:
        st.header("Optimize Existing Post")
        
        original_post = st.text_area(
            "Paste your existing LinkedIn post:",
            height=200,
            placeholder="Paste the LinkedIn post you want to optimize..."
        )
        
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            optimization_goal = st.selectbox(
                "Optimization Goal",
                ["More Engagement", "Professional Tone", "Casual Tone", "Add Hashtags", "Shorten", "Expand"]
            )
        
        with col_opt2:
            st.markdown("**Optimization Tips:**")
            tips = {
                "More Engagement": "Adds questions, calls-to-action, and engaging hooks",
                "Professional Tone": "Makes content more business-appropriate",
                "Casual Tone": "Makes content more conversational and relatable",
                "Add Hashtags": "Includes relevant and trending hashtags",
                "Shorten": "Makes content more concise",
                "Expand": "Adds more detail and context"
            }
            st.info(tips.get(optimization_goal, ""))
        
        if st.button("✨ Optimize Post", type="primary", use_container_width=True):
            if not getattr(st.session_state, 'ai_initialized', False):
                st.error("Please configure your OpenAI API key first!")
            elif not original_post:
                st.error("Please paste a post to optimize!")
            else:
                try:
                    with st.spinner("AI is optimizing your post..."):
                        optimized_post = st.session_state.generator.optimize_post(original_post, optimization_goal)
                        
                        # Display comparison
                        st.markdown("---")
                        col_before, col_after = st.columns(2)
                        
                        with col_before:
                            st.subheader("📄 Original Post")
                            st.text_area("Original:", original_post, height=250, disabled=True, key="original")
                        
                        with col_after:
                            st.subheader("✨ Optimized Post")
                            st.text_area("Optimized:", optimized_post, height=250, key="optimized")
                        
                        # Download button
                        st.download_button(
                            "📥 Download Optimized Post",
                            optimized_post,
                            f"optimized_post_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                        )
                
                except Exception as e:
                    st.error(f"Error optimizing post: {str(e)}")
    
    with tab3:
        st.header("Bulk Post Generator")
        
        st.info("Generate multiple posts at once - perfect for content planning!")
        
        col_bulk1, col_bulk2 = st.columns(2)
        
        with col_bulk1:
            bulk_topics = st.text_area(
                "Topics (one per line):",
                height=150,
                placeholder="AI in Healthcare\nRemote Work Benefits\nDigital Marketing Trends\nLeadership Tips"
            )
            
            bulk_quantity = st.slider("Posts per topic", 1, 5, 2)
        
        with col_bulk2:
            bulk_post_types = st.multiselect(
                "Post Types",
                ["Professional Insights", "Tips & Advice", "Question/Discussion", "Success Story"],
                default=["Tips & Advice", "Question/Discussion"]
            )
            
            bulk_tone = st.selectbox("Tone for all posts", ["Professional", "Conversational", "Educational"])
            bulk_length = st.selectbox("Length for all posts", ["Short (50-100 words)", "Medium (100-200 words)"])
        
        if st.button("🔄 Generate Bulk Posts", type="primary"):
            if not getattr(st.session_state, 'ai_initialized', False):
                st.error("Please configure your OpenAI API key first!")
            elif not bulk_topics.strip():
                st.error("Please enter at least one topic!")
            else:
                topics_list = [topic.strip() for topic in bulk_topics.split('\n') if topic.strip()]
                
                with st.spinner(f"Generating {len(topics_list) * bulk_quantity} posts..."):
                    all_posts = []
                    
                    for topic in topics_list:
                        for i in range(bulk_quantity):
                            try:
                                post_type = bulk_post_types[i % len(bulk_post_types)]
                                
                                if post_type == "Professional Insights":
                                    post = st.session_state.generator.generate_professional_post(
                                        topic, "Professionals", bulk_tone.lower(), 
                                        bulk_length.split()[0].lower(), ""
                                    )
                                else:
                                    post = st.session_state.generator.generate_engagement_post(
                                        post_type.split()[0], topic, ""
                                    )
                                
                                all_posts.append({
                                    'Topic': topic,
                                    'Type': post_type,
                                    'Post': post
                                })
                                
                            except Exception as e:
                                st.error(f"Error generating post for {topic}: {str(e)}")
                    
                    # Display results
                    st.markdown("---")
                    st.subheader(f"📚 Generated {len(all_posts)} Posts")
                    
                    for i, post_data in enumerate(all_posts):
                        with st.expander(f"Post {i+1}: {post_data['Topic']} - {post_data['Type']}"):
                            st.text_area(f"Post {i+1}:", post_data['Post'], height=200, key=f"bulk_post_{i}")
                    
                    # Download all posts
                    if all_posts:
                        bulk_content = "\n\n" + "="*50 + "\n\n".join([
                            f"TOPIC: {post['Topic']}\nTYPE: {post['Type']}\n\n{post['Post']}"
                            for post in all_posts
                        ])
                        
                        st.download_button(
                            "📥 Download All Posts",
                            bulk_content,
                            f"bulk_linkedin_posts_{datetime.now().strftime('%Y%m%d')}.txt"
                        )
    
    with tab4:
        st.header("💡 Content Ideas & Best Practices")
        
        col_ideas1, col_ideas2 = st.columns(2)
        
        with col_ideas1:
            st.subheader("📊 High-Engagement Post Types")
            engagement_data = {
                'Post Type': ['Tips & Lists', 'Questions', 'Behind-the-Scenes', 'Industry News', 'Personal Stories'],
                'Avg. Engagement': ['8.5%', '7.2%', '6.8%', '5.9%', '8.1%'],
                'Best Time': ['9-10 AM', '12-1 PM', '5-6 PM', '8-9 AM', '7-8 PM']
            }
            st.dataframe(pd.DataFrame(engagement_data))
            
            st.subheader("🏷️ Trending Hashtags")
            trending_hashtags = [
                "#AI", "#RemoteWork", "#Leadership", "#Innovation", "#DigitalTransformation",
                "#Sustainability", "#DataScience", "#Entrepreneurship", "#PersonalBranding", "#FutureOfWork"
            ]
            st.write(" ".join([f"`{tag}`" for tag in trending_hashtags]))
        
        with col_ideas2:
            st.subheader("📝 Content Calendar Ideas")
            
            content_ideas = {
                "Monday": "Motivation Monday - Inspirational quotes/stories",
                "Tuesday": "Tips Tuesday - Industry tips and advice", 
                "Wednesday": "Wisdom Wednesday - Lessons learned",
                "Thursday": "Thought Thursday - Industry insights",
                "Friday": "Feature Friday - Highlight achievements",
                "Weekend": "Personal posts - Behind the scenes"
            }
            
            for day, idea in content_ideas.items():
                st.write(f"**{day}:** {idea}")
            
            st.subheader("🎯 Best Practices")
            best_practices = [
                "Post consistently (3-5 times per week)",
                "Use native video when possible",
                "Engage with comments within 1-2 hours",
                "Keep posts between 150-300 characters",
                "Use 3-5 relevant hashtags",
                "Include a clear call-to-action",
                "Share personal experiences and insights",
                "Post during peak engagement hours"
            ]
            
            for practice in best_practices:
                st.write(f"✅ {practice}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💼 Professional LinkedIn Content Creation | Powered by OpenAI GPT</p>
        <p>Perfect for Fiverr services - create engaging content that drives professional growth</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
