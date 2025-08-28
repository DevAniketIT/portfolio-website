# 💼 Job Application Tracker

[![App Status](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fyour-streamlit-app.streamlit.app)](https://your-streamlit-app.streamlit.app)
[![Uptime](https://img.shields.io/uptimerobot/ratio/m{{UPTIMEROBOT_MONITOR_ID}}?label=uptime)](https://stats.uptimerobot.com/{{UPTIMEROBOT_STATUS_PAGE_ID}})
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)

A comprehensive web application built with Python and Streamlit to optimize your job search process. Track applications, analyze patterns, generate cover letters, and never miss a follow-up!

🔗 **[Live Demo](https://your-streamlit-app.streamlit.app)** | 📋 **[View Status](https://stats.uptimerobot.com/{{STATUS_PAGE}})**

## 🌟 Features

### Core Functionality
- **📊 Dashboard**: Visual overview of your job search progress
- **➕ Application Management**: Add, edit, and track job applications
- **📈 Analytics**: Detailed insights into your application patterns
- **⏰ Follow-up Management**: Never miss important follow-ups

### Smart Tools
- **🔗 Auto-Fill from URLs**: Extract job information from posting URLs
- **📄 Cover Letter Generator**: AI-powered cover letters with multiple templates
- **📧 Follow-up Email Templates**: Professional follow-up emails
- **📊 Rejection Analysis**: Learn from rejection patterns to improve

### Data & Export
- **💾 SQLite Database**: Local data storage for privacy
- **📥 Excel Export**: Export your data for external analysis
- **📋 Filtering & Search**: Find applications quickly
- **📱 Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd job-application-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

## 🔧 Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Database**: SQLite (local file database)
- **Visualization**: Plotly (interactive charts)
- **Data Processing**: Pandas
- **Web Scraping**: BeautifulSoup + Requests
- **Deployment**: Streamlit Cloud (free tier)

## 📱 Application Structure

```
job-application-tracker/
├── app.py                  # Main Streamlit application
├── database.py            # SQLite database operations
├── job_utils.py           # Job scraping and auto-fill utilities
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit configuration
└── README.md             # This file
```

## 🎯 Usage Guide

### 1. Adding Applications
- Use "Add Application" from the sidebar
- Optionally paste a job URL to auto-extract information
- Fill in the form with job details
- Set follow-up reminders

### 2. Auto-Fill Tools
- **Job Info Extractor**: Paste URLs from LinkedIn, Indeed, company sites
- **Cover Letter Generator**: Choose from templates (Software Developer, Data Analyst, etc.)
- **Follow-up Emails**: Generate professional follow-up messages

### 3. Analytics & Insights
- **Dashboard**: Overview of your job search metrics
- **Analytics**: Detailed breakdowns by status, company, timeline
- **Rejection Analysis**: Learn from patterns to improve success rate

### 4. Follow-up Management
- View pending follow-ups on the dashboard
- Set custom reminders for each application
- Mark follow-ups as completed

## 🌐 Deployment to Streamlit Cloud

### Free Deployment Steps:

1. **Prepare your code**
   - Ensure all files are in your project directory
   - Test locally with `streamlit run app.py`

2. **Create a GitHub repository**
   - Push your code to a public GitHub repository
   - Include all files: `app.py`, `database.py`, `job_utils.py`, `requirements.txt`

3. **Deploy to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository and branch
   - Set main file path: `app.py`
   - Click "Deploy!"

4. **Your app will be live**
   - Get a public URL like `https://your-app.streamlit.app`
   - Share with potential employers!
   - Monitor uptime with integrated health checks

### Environment Variables (Optional)
If you add external APIs later, you can set secrets in Streamlit Cloud:
- Go to your app settings
- Add secrets in the "Secrets" tab
- Format as TOML

## 📊 Database Schema

The application uses SQLite with three main tables:

### Applications Table
- `id`: Primary key
- `company_name`: Company name
- `job_title`: Position title
- `job_url`: Link to job posting
- `application_date`: When you applied
- `status`: Current status (Applied, Interview, etc.)
- `salary_range`: Expected compensation
- `location`: Job location
- `job_description`: Full job description
- `contact_person`: Recruiter/HR contact
- `notes`: Your notes
- `follow_up_date`: Next follow-up date
- `rejection_reason`: If rejected, why
- `source`: Where you found the job

### Follow-ups Table
- Links to applications
- Tracks follow-up reminders
- Marks completion status

### Interviews Table
- Future enhancement for interview tracking
- Links to applications

## 🔒 Privacy & Security

- **Local Data Storage**: All data stored locally in SQLite
- **No Cloud Dependencies**: Works entirely offline
- **Export Control**: You own and control your data
- **Optional Analytics**: Google Analytics only if environment variable is set
- **Secure Deployment**: HTTPS-only connections in production

## 🎨 Customization

### Adding New Features
1. **New Status Types**: Edit the status dropdown in `app.py`
2. **Custom Templates**: Add templates in `job_utils.py`
3. **New Metrics**: Extend the analytics in `database.py`

### Styling
- Modify CSS in `app.py` for custom colors
- Update `.streamlit/config.toml` for theme changes
- Add custom charts with Plotly

## 📈 Portfolio Impact

This project demonstrates:

### Technical Skills
- **Python Development**: Clean, modular code structure
- **Web Development**: Full-stack application with database
- **Data Analysis**: Pandas, SQL, data visualization
- **UI/UX Design**: User-friendly interface design
- **DevOps**: Deployment and configuration management

### Problem-Solving Approach
- **Identified Pain Point**: Job search tracking inefficiency
- **Built Solution**: Comprehensive tracking system
- **Added Value**: Analytics and automation features
- **Real-world Usage**: Immediately useful tool

### Professional Narrative
*"I built this Job Application Tracker to solve my own job search challenges. It demonstrates my ability to identify problems, architect solutions, and build production-ready applications. The tool has helped me stay organized and analyze my job search patterns for better results."*

## 🚀 Future Enhancements

### Potential Additions
- **Email Integration**: Import applications from email
- **Calendar Sync**: Sync follow-ups with Google Calendar
- **Resume Matching**: Score resume match against job descriptions
- **Salary Insights**: Market rate analysis
- **Interview Prep**: Company research automation
- **Application Templates**: Save and reuse application data

### Advanced Analytics
- **Success Prediction**: ML model for application success
- **Market Trends**: Industry hiring pattern analysis
- **Skill Gap Analysis**: Identify missing qualifications
- **Geographic Analysis**: Location-based success rates

## 🤝 Contributing

This is a personal portfolio project, but improvements are welcome!

1. Fork the repository
2. Create a feature branch
3. Make improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and adapt for your own needs.

## 📞 Contact

Built by **Aniket Kumar** as part of a comprehensive Python development portfolio.

- **Portfolio**: [aniket-portfolio.vercel.app](https://aniket-portfolio.vercel.app)
- **LinkedIn**: [linkedin.com/in/aniket-kumar-devpro](https://linkedin.com/in/aniket-kumar-devpro)
- **GitHub**: [github.com/DevAniketIT](https://github.com/DevAniketIT)
- **Email**: [aniket.kumar.devpro@gmail.com](mailto:aniket.kumar.devpro@gmail.com)

---

## 🎯 Why This Project Matters

In today's competitive job market, organization and data-driven decision making are crucial for job search success. This application:

1. **Eliminates Manual Tracking**: No more spreadsheets or scattered notes
2. **Provides Actionable Insights**: Learn what works and what doesn't
3. **Saves Time**: Auto-fill tools and templates speed up applications
4. **Improves Follow-up**: Never miss important follow-up opportunities
5. **Demonstrates Skills**: Shows technical ability while solving real problems

The project showcases full-stack development skills while addressing a genuine professional need - making it a perfect portfolio piece that tells a compelling story about problem-solving and technical execution.

**Start tracking your job applications today and turn your job search into a data-driven process!** 🚀
