import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os

from database import JobApplicationDB
from job_utils import JobInfoScraper, AutoFillGenerator

# Page configuration
st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and utilities
@st.cache_resource
def init_database():
    return JobApplicationDB()

@st.cache_resource
def init_scraper():
    return JobInfoScraper()

@st.cache_resource
def init_auto_fill():
    return AutoFillGenerator()

db = init_database()
scraper = init_scraper()
auto_fill = init_auto_fill()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-applied { color: #ff7f0e; }
    .status-interview { color: #2ca02c; }
    .status-offer { color: #1f77b4; }
    .status-rejected { color: #d62728; }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🎯 Job Tracker")
page = st.sidebar.selectbox(
    "Navigate to:",
    ["🏠 Dashboard", "➕ Add Application", "📋 View Applications", "📊 Analytics", 
     "📝 Auto-Fill Tools", "⏰ Follow-ups", "📈 Rejection Analysis"]
)

# Helper functions
def get_status_color(status):
    colors = {
        'Applied': '#ff7f0e',
        'Interview Scheduled': '#2ca02c',
        'Interview Completed': '#2ca02c',
        'Offer Received': '#1f77b4',
        'Hired': '#17becf',
        'Rejected': '#d62728',
        'Withdrawn': '#7f7f7f'
    }
    return colors.get(status, '#7f7f7f')

def display_application_card(row):
    status_color = get_status_color(row['status'])
    
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.markdown(f"**{row['company_name']}** - {row['job_title']}")
            if row['location']:
                st.caption(f"📍 {row['location']}")
        
        with col2:
            st.write(f"Applied: {row['application_date']}")
            if row['salary_range']:
                st.caption(f"💰 {row['salary_range']}")
        
        with col3:
            st.markdown(f"<span style='color:{status_color}'>●</span> **{row['status']}**", 
                       unsafe_allow_html=True)
        
        with col4:
            if st.button("Edit", key=f"edit_{row['id']}"):
                st.session_state.edit_app_id = row['id']
        
        st.divider()

# Main app logic
if page == "🏠 Dashboard":
    st.markdown("<h1 class='main-header'>Job Application Dashboard</h1>", unsafe_allow_html=True)
    
    # Get statistics
    stats = db.get_application_stats()
    
    if stats['total_applications'] == 0:
        st.info("👋 Welcome! Start by adding your first job application using the sidebar.")
        st.markdown("### Quick Start Guide:")
        st.markdown("""
        1. **Add Application** - Record your job applications
        2. **Auto-Fill Tools** - Generate cover letters and extract job info from URLs
        3. **Track Follow-ups** - Never miss a follow-up opportunity  
        4. **Analyze Patterns** - Learn from your application data
        """)
    else:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Applications", stats['total_applications'])
        
        with col2:
            st.metric("Response Rate", f"{stats['response_rate']:.1f}%")
        
        with col3:
            pending_followups = len(db.get_pending_followups())
            st.metric("Pending Follow-ups", pending_followups)
        
        with col4:
            recent_apps = len(db.get_all_applications()[
                db.get_all_applications()['application_date'] >= 
                (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            ])
            st.metric("This Week", recent_apps)
        
        # Status breakdown chart
        if not stats['status_breakdown'].empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Application Status")
                fig_pie = px.pie(
                    stats['status_breakdown'], 
                    values='count', 
                    names='status',
                    color='status',
                    color_discrete_map={
                        'Applied': '#ff7f0e',
                        'Interview Scheduled': '#2ca02c',
                        'Interview Completed': '#2ca02c', 
                        'Offer Received': '#1f77b4',
                        'Hired': '#17becf',
                        'Rejected': '#d62728',
                        'Withdrawn': '#7f7f7f'
                    }
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("Monthly Applications")
                if not stats['monthly_applications'].empty:
                    fig_bar = px.bar(
                        stats['monthly_applications'],
                        x='month',
                        y='applications',
                        color='applications',
                        color_continuous_scale='Blues'
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        # Recent applications
        st.subheader("Recent Applications")
        recent_df = db.get_all_applications().head(5)
        
        if not recent_df.empty:
            for _, row in recent_df.iterrows():
                display_application_card(row)
        else:
            st.info("No applications yet. Add your first one!")

elif page == "➕ Add Application":
    st.header("Add New Job Application")
    
    # URL extraction section
    st.subheader("🔗 Auto-Extract Job Info (Optional)")
    job_url = st.text_input("Job Posting URL", placeholder="https://company.com/jobs/123")
    
    if job_url and st.button("Extract Job Information"):
        with st.spinner("Extracting job information..."):
            job_info = scraper.extract_job_info(job_url)
            
            if job_info['title']:
                st.success("✅ Job information extracted!")
                
                # Store extracted info in session state
                st.session_state.extracted_info = job_info
                st.session_state.job_url = job_url
                
                # Display extracted info
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Title:**", job_info['title'])
                    st.write("**Company:**", job_info['company'])
                with col2:
                    st.write("**Location:**", job_info['location'])
                    st.write("**Salary:**", job_info['salary'])
                
                if job_info['description']:
                    st.text_area("Description Preview", job_info['description'][:500] + "...", disabled=True)
            else:
                st.warning("Could not extract job information. Please fill in manually.")
    
    st.divider()
    
    # Application form
    with st.form("add_application"):
        st.subheader("📝 Application Details")
        
        # Pre-fill with extracted info if available
        extracted = st.session_state.get('extracted_info', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", value=extracted.get('company', ''))
            job_title = st.text_input("Job Title *", value=extracted.get('title', ''))
            location = st.text_input("Location", value=extracted.get('location', ''))
            source = st.selectbox("Application Source", 
                                ["LinkedIn", "Indeed", "Company Website", "Referral", "Recruiter", "Other"])
        
        with col2:
            application_date = st.date_input("Application Date", value=date.today())
            status = st.selectbox("Status", 
                                ["Applied", "Interview Scheduled", "Interview Completed", 
                                 "Offer Received", "Rejected", "Withdrawn"])
            salary_range = st.text_input("Salary Range", value=extracted.get('salary', ''))
            follow_up_date = st.date_input("Follow-up Date", 
                                         value=date.today() + timedelta(days=7))
        
        # Contact information
        st.subheader("👥 Contact Information")
        col3, col4 = st.columns(2)
        
        with col3:
            contact_person = st.text_input("Contact Person")
        with col4:
            contact_email = st.text_input("Contact Email")
        
        # Job details
        job_description = st.text_area("Job Description", 
                                     value=extracted.get('description', ''),
                                     height=150)
        notes = st.text_area("Notes", height=100)
        
        submitted = st.form_submit_button("Add Application", type="primary")
        
        if submitted:
            if company_name and job_title:
                application_data = {
                    'company_name': company_name,
                    'job_title': job_title,
                    'job_url': st.session_state.get('job_url', ''),
                    'application_date': application_date.strftime('%Y-%m-%d'),
                    'status': status,
                    'salary_range': salary_range,
                    'location': location,
                    'job_description': job_description,
                    'contact_person': contact_person,
                    'contact_email': contact_email,
                    'notes': notes,
                    'follow_up_date': follow_up_date.strftime('%Y-%m-%d'),
                    'source': source
                }
                
                app_id = db.add_application(application_data)
                st.success(f"✅ Application added successfully! ID: {app_id}")
                
                # Clear session state
                if 'extracted_info' in st.session_state:
                    del st.session_state.extracted_info
                if 'job_url' in st.session_state:
                    del st.session_state.job_url
                
                st.rerun()
            else:
                st.error("Please fill in required fields (Company Name and Job Title)")

elif page == "📋 View Applications":
    st.header("All Applications")
    
    applications = db.get_all_applications()
    
    if applications.empty:
        st.info("No applications yet. Add your first one!")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=applications['status'].unique(),
                default=applications['status'].unique()
            )
        
        with col2:
            company_filter = st.multiselect(
                "Filter by Company",
                options=sorted(applications['company_name'].unique())
            )
        
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=[],
                max_value=date.today()
            )
        
        # Apply filters
        filtered_df = applications.copy()
        
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        
        if company_filter:
            filtered_df = filtered_df[filtered_df['company_name'].isin(company_filter)]
        
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (pd.to_datetime(filtered_df['application_date']) >= pd.to_datetime(start_date)) &
                (pd.to_datetime(filtered_df['application_date']) <= pd.to_datetime(end_date))
            ]
        
        st.write(f"Showing {len(filtered_df)} of {len(applications)} applications")
        
        # Display applications
        for _, row in filtered_df.iterrows():
            display_application_card(row)
        
        # Export functionality
        if st.button("📥 Export to Excel"):
            excel_file = f"job_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filtered_df.to_excel(excel_file, index=False)
            st.success(f"Exported to {excel_file}")

elif page == "📊 Analytics":
    st.header("Job Application Analytics")
    
    stats = db.get_application_stats()
    
    if stats['total_applications'] == 0:
        st.info("Add some applications to see analytics!")
    else:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        applications_df = db.get_all_applications()
        
        with col1:
            st.metric("Total Applications", stats['total_applications'])
        
        with col2:
            st.metric("Response Rate", f"{stats['response_rate']:.1f}%")
        
        with col3:
            avg_per_week = len(applications_df) / max(1, 
                (datetime.now() - pd.to_datetime(applications_df['application_date']).min()).days / 7)
            st.metric("Avg/Week", f"{avg_per_week:.1f}")
        
        with col4:
            interviews = len(applications_df[applications_df['status'].isin(['Interview Scheduled', 'Interview Completed'])])
            interview_rate = (interviews / len(applications_df) * 100) if len(applications_df) > 0 else 0
            st.metric("Interview Rate", f"{interview_rate:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            st.subheader("Application Status Distribution")
            if not stats['status_breakdown'].empty:
                fig_pie = px.pie(
                    stats['status_breakdown'], 
                    values='count', 
                    names='status',
                    color='status',
                    color_discrete_map={
                        'Applied': '#ff7f0e',
                        'Interview Scheduled': '#2ca02c',
                        'Interview Completed': '#2ca02c',
                        'Offer Received': '#1f77b4',
                        'Hired': '#17becf',
                        'Rejected': '#d62728',
                        'Withdrawn': '#7f7f7f'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Applications by source
            st.subheader("Applications by Source")
            source_breakdown = applications_df['source'].value_counts()
            if not source_breakdown.empty:
                fig_source = px.bar(
                    x=source_breakdown.index,
                    y=source_breakdown.values,
                    color=source_breakdown.values,
                    color_continuous_scale='Viridis'
                )
                fig_source.update_layout(showlegend=False, xaxis_title="Source", yaxis_title="Count")
                st.plotly_chart(fig_source, use_container_width=True)
        
        # Timeline analysis
        st.subheader("Application Timeline")
        if not stats['monthly_applications'].empty:
            fig_timeline = px.line(
                stats['monthly_applications'],
                x='month',
                y='applications',
                title="Applications Over Time",
                markers=True
            )
            fig_timeline.update_layout(xaxis_title="Month", yaxis_title="Number of Applications")
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Company analysis
        st.subheader("Top Companies Applied To")
        company_counts = applications_df['company_name'].value_counts().head(10)
        
        if not company_counts.empty:
            fig_companies = px.bar(
                x=company_counts.values,
                y=company_counts.index,
                orientation='h',
                title="Applications by Company"
            )
            fig_companies.update_layout(xaxis_title="Number of Applications", yaxis_title="Company")
            st.plotly_chart(fig_companies, use_container_width=True)

elif page == "📝 Auto-Fill Tools":
    st.header("Auto-Fill Tools")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Job Info Extractor", "📄 Cover Letter Generator", "📧 Follow-up Email"])
    
    with tab1:
        st.subheader("Extract Job Information from URL")
        st.write("Paste a job posting URL to automatically extract key information.")
        
        job_url = st.text_input("Job URL", placeholder="https://company.com/careers/position")
        
        if job_url and st.button("Extract Information", key="extract_info"):
            with st.spinner("Extracting job information..."):
                job_info = scraper.extract_job_info(job_url)
                
                if job_info['title']:
                    st.success("✅ Information extracted successfully!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text_input("Job Title", value=job_info['title'])
                        st.text_input("Company", value=job_info['company'])
                        st.text_input("Location", value=job_info['location'])
                    
                    with col2:
                        st.text_input("Salary Range", value=job_info['salary'])
                        st.text_area("Description", value=job_info['description'][:500] + "..." if len(job_info['description']) > 500 else job_info['description'])
                    
                    if st.button("Add to Applications"):
                        st.session_state.extracted_info = job_info
                        st.session_state.job_url = job_url
                        st.success("Information saved! Go to 'Add Application' to complete the form.")
                else:
                    st.error("Could not extract information from this URL. The site may be protected or the format unsupported.")
    
    with tab2:
        st.subheader("Generate Cover Letter")
        
        # Personal information
        with st.expander("👤 Personal Information (Save for reuse)"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Your Name", value="[Your Name]")
                experience_years = st.text_input("Years of Experience", value="X")
            
            with col2:
                key_skills = st.text_input("Key Skills", value="Python, Data Analysis, etc.")
                relevant_experience = st.text_area("Relevant Experience Summary", 
                                                 value="[Describe your most relevant experience]")
        
        # Job information
        st.subheader("Job Details")
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title", value="")
            company_name = st.text_input("Company Name", value="")
        
        with col2:
            template_type = st.selectbox("Template Type", 
                                       ["general", "software_developer", "data_analyst", "project_manager"])
        
        if st.button("Generate Cover Letter"):
            job_info = {'title': job_title, 'company': company_name}
            personal_info = {
                'name': name,
                'experience_years': experience_years,
                'key_skills': key_skills,
                'relevant_experience': relevant_experience
            }
            
            cover_letter = auto_fill.generate_cover_letter(job_info, template_type, personal_info)
            
            st.subheader("Generated Cover Letter")
            st.text_area("Cover Letter", value=cover_letter, height=400)
            
            # Copy to clipboard functionality would require additional JavaScript
            st.info("💡 Copy the text above and paste it into your application!")
    
    with tab3:
        st.subheader("Generate Follow-up Email")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title", key="followup_title")
            company_name = st.text_input("Company Name", key="followup_company")
        
        with col2:
            days_since = st.number_input("Days Since Application", min_value=1, value=7)
        
        if st.button("Generate Follow-up Email"):
            job_info = {'title': job_title, 'company': company_name}
            follow_up_email = auto_fill.generate_follow_up_email(job_info, days_since)
            
            st.subheader("Generated Follow-up Email")
            st.text_area("Follow-up Email", value=follow_up_email, height=300)

elif page == "⏰ Follow-ups":
    st.header("Follow-up Management")
    
    # Pending follow-ups
    pending_followups = db.get_pending_followups()
    
    if not pending_followups.empty:
        st.subheader("🔥 Pending Follow-ups")
        
        for _, followup in pending_followups.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{followup['company_name']}** - {followup['job_title']}")
                    st.caption(followup['notes'] if followup['notes'] else "No notes")
                
                with col2:
                    st.write(f"Due: {followup['follow_up_date']}")
                    st.caption(f"Type: {followup['follow_up_type']}")
                
                with col3:
                    days_overdue = (datetime.now().date() - pd.to_datetime(followup['follow_up_date']).date()).days
                    if days_overdue > 0:
                        st.error(f"⚠️ {days_overdue} days overdue")
                    else:
                        st.success("📅 Due today")
                
                with col4:
                    if st.button("Mark Done", key=f"complete_{followup['id']}"):
                        db.complete_followup(followup['id'])
                        st.rerun()
                
                st.divider()
    else:
        st.info("🎉 No pending follow-ups!")
    
    # Add new follow-up
    st.subheader("➕ Add Follow-up Reminder")
    
    applications = db.get_all_applications()
    
    if not applications.empty:
        with st.form("add_followup"):
            app_options = [f"{row['company_name']} - {row['job_title']} (ID: {row['id']})" 
                          for _, row in applications.iterrows()]
            
            selected_app = st.selectbox("Select Application", app_options)
            
            col1, col2 = st.columns(2)
            
            with col1:
                followup_date = st.date_input("Follow-up Date", value=date.today() + timedelta(days=7))
                followup_type = st.selectbox("Follow-up Type", 
                                           ["Email", "Phone Call", "LinkedIn Message", "Application Status Check"])
            
            with col2:
                notes = st.text_area("Notes", placeholder="What to follow up about...")
            
            if st.form_submit_button("Add Follow-up"):
                app_id = int(selected_app.split("ID: ")[1].split(")")[0])
                db.add_followup(app_id, followup_date.strftime('%Y-%m-%d'), followup_type, notes)
                st.success("Follow-up reminder added!")
                st.rerun()
    else:
        st.info("Add some applications first to create follow-ups!")

elif page == "📈 Rejection Analysis":
    st.header("Rejection Pattern Analysis")
    
    rejection_analysis = db.get_rejection_analysis()
    
    if rejection_analysis['rejection_reasons'].empty and rejection_analysis['time_to_rejection'].empty:
        st.info("No rejection data available yet. Update application statuses to see analysis.")
    else:
        # Rejection reasons
        if not rejection_analysis['rejection_reasons'].empty:
            st.subheader("🎯 Common Rejection Reasons")
            
            fig_reasons = px.bar(
                rejection_analysis['rejection_reasons'],
                x='count',
                y='rejection_reason',
                orientation='h',
                title="Most Common Rejection Reasons"
            )
            st.plotly_chart(fig_reasons, use_container_width=True)
        
        # Time to rejection analysis
        if not rejection_analysis['time_to_rejection'].empty:
            st.subheader("⏱️ Time to Rejection Analysis")
            
            time_df = rejection_analysis['time_to_rejection']
            avg_days = time_df['days_to_rejection'].mean()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Average Days to Rejection", f"{avg_days:.1f}")
            
            with col2:
                fastest_rejection = time_df['days_to_rejection'].min()
                st.metric("Fastest Rejection", f"{fastest_rejection:.0f} days")
            
            # Histogram of rejection times
            fig_hist = px.histogram(
                time_df,
                x='days_to_rejection',
                nbins=20,
                title="Distribution of Days to Rejection"
            )
            fig_hist.update_layout(xaxis_title="Days to Rejection", yaxis_title="Count")
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Recent rejections
            st.subheader("Recent Rejections")
            recent_rejections = time_df.head(10)
            
            for _, rejection in recent_rejections.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**{rejection['company_name']}**")
                        st.caption(rejection['job_title'])
                    
                    with col2:
                        st.write(f"Applied: {rejection['application_date']}")
                        st.caption(f"Rejected: {rejection['updated_at'][:10]}")
                    
                    with col3:
                        st.metric("Days", f"{rejection['days_to_rejection']:.0f}")
                    
                    st.divider()
        
        # Actionable insights
        st.subheader("🔍 Insights & Recommendations")
        
        applications = db.get_all_applications()
        
        if not applications.empty:
            total_apps = len(applications)
            rejected_apps = len(applications[applications['status'] == 'Rejected'])
            
            if rejected_apps > 0:
                rejection_rate = (rejected_apps / total_apps) * 100
                
                insights = []
                
                if rejection_rate > 70:
                    insights.append("🎯 High rejection rate - consider refining your target roles or improving application materials")
                elif rejection_rate > 50:
                    insights.append("📝 Moderate rejection rate - review your resume and cover letter templates")
                else:
                    insights.append("✅ Good rejection rate - keep up the current strategy!")
                
                if avg_days < 3:
                    insights.append("⚡ Quick rejections may indicate resume screening issues - optimize for ATS")
                elif avg_days > 14:
                    insights.append("⏳ Slow rejections suggest you're passing initial screening - focus on interview prep")
                
                # Display insights
                for insight in insights:
                    st.info(insight)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tips:**")
st.sidebar.markdown("- Update statuses regularly")
st.sidebar.markdown("- Set follow-up reminders")
st.sidebar.markdown("- Use auto-fill tools to save time")
st.sidebar.markdown("- Review analytics weekly")

# Add some spacing
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("Built with ❤️ using Streamlit")
