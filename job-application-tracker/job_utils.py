import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse
import time

class JobInfoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_job_info(self, url):
        """
        Extract job information from a job posting URL
        Works with various job sites like LinkedIn, Indeed, etc.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_info = {
                'title': self._extract_title(soup, url),
                'company': self._extract_company(soup, url),
                'location': self._extract_location(soup, url),
                'salary': self._extract_salary(soup, url),
                'description': self._extract_description(soup, url),
                'requirements': self._extract_requirements(soup, url)
            }
            
            return job_info
            
        except Exception as e:
            return {
                'title': '',
                'company': '',
                'location': '',
                'salary': '',
                'description': f'Error extracting job info: {str(e)}',
                'requirements': ''
            }
    
    def _extract_title(self, soup, url):
        """Extract job title from various job sites"""
        selectors = [
            'h1[data-automation-id="jobPostingHeader"]',  # Workday
            'h1.jobsearch-JobInfoHeader-title',  # Indeed
            'h1.top-card-layout__title',  # LinkedIn
            'h1.job-title',
            'h1[class*="title"]',
            'h1',
            '[data-testid="job-title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return ''
    
    def _extract_company(self, soup, url):
        """Extract company name"""
        selectors = [
            '[data-automation-id="jobPostingCompany"]',  # Workday
            'span.jobsearch-InlineCompanyRating',  # Indeed
            'a.topcard__org-name-link',  # LinkedIn
            '.company-name',
            '[class*="company"]',
            '[data-testid="company-name"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Try to extract from URL domain
        domain = urlparse(url).netloc
        if domain:
            company = domain.replace('www.', '').replace('.com', '').replace('.careers', '')
            return company.title()
        
        return ''
    
    def _extract_location(self, soup, url):
        """Extract job location"""
        selectors = [
            '[data-automation-id="jobPostingLocation"]',
            'div[data-testid="job-location"]',
            '.jobsearch-JobInfoHeader-subtitle',
            '.topcard__flavor--bullet',
            '[class*="location"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Clean up common location patterns
                if 'Remote' in text or 'Hybrid' in text or any(state in text for state in ['CA', 'NY', 'TX', 'FL']):
                    return text
        
        return ''
    
    def _extract_salary(self, soup, url):
        """Extract salary information"""
        selectors = [
            '[data-automation-id="jobPostingSalary"]',
            '.salary-snippet',
            '[class*="salary"]',
            '[class*="pay"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Look for salary patterns in text
        text = soup.get_text()
        salary_patterns = [
            r'\$[\d,]+ - \$[\d,]+',
            r'\$[\d,]+k - \$[\d,]+k',
            r'\$[\d,]+/year',
            r'\$[\d,]+ per year',
            r'[\d,]+ - [\d,]+ USD'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        return ''
    
    def _extract_description(self, soup, url):
        """Extract job description"""
        selectors = [
            '[data-automation-id="jobPostingDescription"]',
            '#jobDescriptionText',
            '.description',
            '.job-description',
            '[class*="description"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator='\n', strip=True)
                # Limit description length
                return text[:2000] + '...' if len(text) > 2000 else text
        
        return ''
    
    def _extract_requirements(self, soup, url):
        """Extract job requirements"""
        description = self._extract_description(soup, url)
        
        # Look for requirements section
        requirements_patterns = [
            r'Requirements?:(.+?)(?=\n\n|\nResponsibilities|\nQualifications|\nAbout|$)',
            r'Qualifications?:(.+?)(?=\n\n|\nResponsibilities|\nRequirements|\nAbout|$)',
            r'Skills?:(.+?)(?=\n\n|\nResponsibilities|\nRequirements|\nAbout|$)'
        ]
        
        for pattern in requirements_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ''

class AutoFillGenerator:
    """Generate common form data for job applications"""
    
    def __init__(self):
        self.personal_info = {
            'cover_letter_templates': {
                'software_developer': self._software_developer_template,
                'data_analyst': self._data_analyst_template,
                'project_manager': self._project_manager_template,
                'general': self._general_template
            }
        }
    
    def generate_cover_letter(self, job_info, template_type='general', personal_info=None):
        """Generate a customized cover letter"""
        if personal_info is None:
            personal_info = {
                'name': '[Your Name]',
                'experience_years': '[X]',
                'key_skills': '[Your Key Skills]',
                'relevant_experience': '[Your Relevant Experience]'
            }
        
        template_func = self.personal_info['cover_letter_templates'].get(
            template_type, 
            self.personal_info['cover_letter_templates']['general']
        )
        
        return template_func(job_info, personal_info)
    
    def _general_template(self, job_info, personal_info):
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_info.get('title', '[Job Title]')} position at {job_info.get('company', '[Company Name]')}. With {personal_info['experience_years']} years of experience in {personal_info['key_skills']}, I am excited about the opportunity to contribute to your team.

{personal_info['relevant_experience']}

Based on the job requirements, I believe my background in {personal_info['key_skills']} makes me a strong candidate for this role. I am particularly drawn to {job_info.get('company', '[Company Name]')} because of [specific reason - research the company].

I would welcome the opportunity to discuss how my experience and enthusiasm can contribute to your team's success. Thank you for considering my application.

Best regards,
{personal_info['name']}"""

    def _software_developer_template(self, job_info, personal_info):
        return f"""Dear Hiring Manager,

I am excited to apply for the {job_info.get('title', 'Software Developer')} position at {job_info.get('company', '[Company Name]')}. As a passionate developer with {personal_info['experience_years']} years of experience in {personal_info['key_skills']}, I am eager to bring my technical expertise to your innovative team.

In my previous roles, I have successfully {personal_info['relevant_experience']}, developing scalable solutions and collaborating with cross-functional teams to deliver high-quality software products.

The requirements mentioned in your posting align perfectly with my skill set, particularly in {personal_info['key_skills']}. I am excited about the opportunity to contribute to {job_info.get('company', '[Company Name]')}'s mission and help drive technological innovation.

I would love to discuss how my technical background and problem-solving approach can add value to your development team.

Best regards,
{personal_info['name']}"""

    def _data_analyst_template(self, job_info, personal_info):
        return f"""Dear Hiring Manager,

I am writing to apply for the {job_info.get('title', 'Data Analyst')} position at {job_info.get('company', '[Company Name]')}. With {personal_info['experience_years']} years of experience in data analysis, statistical modeling, and {personal_info['key_skills']}, I am confident in my ability to help drive data-driven decision making at your organization.

My experience includes {personal_info['relevant_experience']}, where I have consistently delivered actionable insights that improved business outcomes and operational efficiency.

I am particularly excited about this opportunity because {job_info.get('company', '[Company Name]')} is known for its data-driven approach and commitment to innovation. I believe my analytical skills and passion for uncovering meaningful patterns in data would be valuable assets to your team.

I would welcome the opportunity to discuss how my analytical expertise can contribute to your data initiatives.

Sincerely,
{personal_info['name']}"""

    def _project_manager_template(self, job_info, personal_info):
        return f"""Dear Hiring Manager,

I am pleased to submit my application for the {job_info.get('title', 'Project Manager')} position at {job_info.get('company', '[Company Name]')}. With {personal_info['experience_years']} years of project management experience and expertise in {personal_info['key_skills']}, I am excited about the opportunity to lead successful project delivery at your organization.

Throughout my career, I have {personal_info['relevant_experience']}, consistently delivering projects on time, within budget, and exceeding stakeholder expectations. My approach combines strong organizational skills with collaborative leadership and strategic thinking.

I am drawn to {job_info.get('company', '[Company Name]')} because of your reputation for innovation and excellence. I believe my project management expertise and commitment to continuous improvement would make me a valuable addition to your team.

I look forward to discussing how my experience can contribute to your project success.

Best regards,
{personal_info['name']}"""

    def generate_follow_up_email(self, job_info, days_since_application=7):
        """Generate follow-up email template"""
        return f"""Subject: Following up on {job_info.get('title', '[Job Title]')} Application

Dear Hiring Manager,

I hope this email finds you well. I wanted to follow up on my application for the {job_info.get('title', '[Job Title]')} position at {job_info.get('company', '[Company Name]')} that I submitted {days_since_application} days ago.

I remain very interested in this opportunity and would welcome the chance to discuss how my skills and experience can contribute to your team. If you need any additional information from me, please don't hesitate to reach out.

Thank you for your time and consideration. I look forward to hearing from you soon.

Best regards,
[Your Name]
[Your Phone Number]
[Your Email]"""
