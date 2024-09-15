#!/usr/bin/env python3
"""
AI Chatbot Integration System
Easy-to-implement chatbot solutions for websites.
Services priced between ₹3000-8000 per implementation.
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import openai
from flask import Flask, request, jsonify, render_template_string
import requests
import re

class AIWorkflowChatbot:
    def __init__(self, config_file: str = "chatbot_config.json"):
        """Initialize the AI Chatbot"""
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.setup_database()
        self.app = Flask(__name__)
        self.setup_routes()
    
    def load_config(self, config_file: str) -> Dict:
        """Load chatbot configuration"""
        default_config = {
            "api_key": "",
            "model": "gpt-3.5-turbo",
            "company_name": "Your Company",
            "business_hours": "9 AM - 6 PM",
            "contact_email": "info@yourcompany.com",
            "phone": "+91-9876543210",
            "website": "https://yourcompany.com",
            "services": ["Web Development", "Digital Marketing", "Consulting"],
            "greeting_message": "Hello! How can I help you today?",
            "fallback_message": "I'm sorry, I didn't understand that. Could you please rephrase?",
            "lead_collection": True,
            "analytics": True
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            return default_config
    
    def setup_logging(self):
        """Setup logging for chatbot operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'chatbot_{datetime.now().strftime("%Y%m")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup SQLite database for storing conversations and leads"""
        self.conn = sqlite3.connect('chatbot.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_message TEXT,
                bot_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_email TEXT,
                user_phone TEXT
            )
        ''')
        
        # Leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                message TEXT,
                service_interest TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new'
            )
        ''')
        
        self.conn.commit()
    
    def get_ai_response(self, user_message: str, context: Dict = None) -> str:
        """
        Generate AI response using OpenAI or fallback to rule-based responses
        """
        if not self.config.get('api_key'):
            return self.get_rule_based_response(user_message)
        
        try:
            # Create context-aware prompt
            system_prompt = f"""
            You are a helpful customer service chatbot for {self.config['company_name']}.
            
            Company Information:
            - Services: {', '.join(self.config['services'])}
            - Business Hours: {self.config['business_hours']}
            - Contact: {self.config['contact_email']}, {self.config['phone']}
            - Website: {self.config['website']}
            
            Guidelines:
            - Be helpful, friendly, and professional
            - Provide accurate information about the company
            - If asked about services, mention our offerings
            - For complex queries, suggest contacting us directly
            - Keep responses concise but informative
            - If someone shows interest, try to collect their contact information
            """
            
            openai.api_key = self.config['api_key']
            
            response = openai.ChatCompletion.create(
                model=self.config['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return self.get_rule_based_response(user_message)
    
    def get_rule_based_response(self, user_message: str) -> str:
        """
        Rule-based response system as fallback
        """
        message_lower = user_message.lower()
        
        # Greeting patterns
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in message_lower for greeting in greetings):
            return f"{self.config['greeting_message']} I'm here to help you learn more about {self.config['company_name']}."
        
        # Services inquiry
        if any(word in message_lower for word in ['service', 'services', 'what do you do', 'offerings']):
            services_list = ', '.join(self.config['services'])
            return f"We offer the following services: {services_list}. Which one interests you most?"
        
        # Contact information
        if any(word in message_lower for word in ['contact', 'phone', 'email', 'reach']):
            return f"You can reach us at:\n📧 Email: {self.config['contact_email']}\n📞 Phone: {self.config['phone']}\n🌐 Website: {self.config['website']}"
        
        # Business hours
        if any(word in message_lower for word in ['hours', 'time', 'open', 'available']):
            return f"Our business hours are {self.config['business_hours']}. We're always happy to help during these times!"
        
        # Pricing inquiry
        if any(word in message_lower for word in ['price', 'cost', 'pricing', 'quote']):
            return "Our pricing varies based on your specific needs. Would you like me to connect you with our team for a personalized quote? Please share your contact information."
        
        # Lead collection trigger
        if any(word in message_lower for word in ['interested', 'want to know more', 'tell me more', 'quote']):
            return "I'd love to help you learn more! Could you please share your name and email address so our team can provide you with detailed information?"
        
        return self.config['fallback_message']
    
    def extract_contact_info(self, message: str) -> Dict[str, Optional[str]]:
        """
        Extract email and phone number from user message
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(?:\+91|91)?[-.\s]?(?:\d{5}[-.\s]?\d{5}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\d{10})\b'
        
        email = re.search(email_pattern, message)
        phone = re.search(phone_pattern, message)
        
        return {
            'email': email.group() if email else None,
            'phone': phone.group() if phone else None
        }
    
    def save_conversation(self, session_id: str, user_message: str, bot_response: str, 
                         user_email: str = None, user_phone: str = None):
        """Save conversation to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (session_id, user_message, bot_response, user_email, user_phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_message, bot_response, user_email, user_phone))
        self.conn.commit()
    
    def save_lead(self, name: str, email: str, phone: str = None, 
                  message: str = None, service_interest: str = None):
        """Save lead information to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO leads (name, email, phone, message, service_interest)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, message, service_interest))
        self.conn.commit()
        
        # Send notification (you can implement email/SMS notification here)
        self.logger.info(f"New lead captured: {name} - {email}")
    
    def setup_routes(self):
        """Setup Flask routes for the chatbot"""
        
        @self.app.route('/')
        def index():
            return render_template_string(CHATBOT_HTML_TEMPLATE)
        
        @self.app.route('/chat', methods=['POST'])
        def chat():
            data = request.json
            user_message = data.get('message', '')
            session_id = data.get('session_id', 'anonymous')
            
            if not user_message:
                return jsonify({'error': 'Message is required'}), 400
            
            # Extract contact information if available
            contact_info = self.extract_contact_info(user_message)
            
            # Generate response
            bot_response = self.get_ai_response(user_message)
            
            # Save conversation
            self.save_conversation(
                session_id, user_message, bot_response, 
                contact_info.get('email'), contact_info.get('phone')
            )
            
            # Check if this looks like a lead (has contact info)
            if contact_info['email']:
                # Try to extract name from the message
                name_patterns = [
                    r'my name is ([a-zA-Z\s]+)',
                    r'i am ([a-zA-Z\s]+)',
                    r'i\'m ([a-zA-Z\s]+)'
                ]
                
                name = None
                for pattern in name_patterns:
                    match = re.search(pattern, user_message.lower())
                    if match:
                        name = match.group(1).strip().title()
                        break
                
                if not name:
                    name = "Unknown"
                
                self.save_lead(
                    name, contact_info['email'], contact_info.get('phone'), 
                    user_message, "General Inquiry"
                )
            
            return jsonify({
                'response': bot_response,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/leads')
        def get_leads():
            """Get all leads (admin endpoint)"""
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM leads ORDER BY timestamp DESC')
            leads = cursor.fetchall()
            
            return jsonify({
                'leads': [
                    {
                        'id': lead[0],
                        'name': lead[1],
                        'email': lead[2],
                        'phone': lead[3],
                        'message': lead[4],
                        'service_interest': lead[5],
                        'timestamp': lead[6],
                        'status': lead[7]
                    }
                    for lead in leads
                ]
            })
        
        @self.app.route('/analytics')
        def get_analytics():
            """Get chatbot analytics"""
            cursor = self.conn.cursor()
            
            # Total conversations
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            # Total leads
            cursor.execute('SELECT COUNT(*) FROM leads')
            total_leads = cursor.fetchone()[0]
            
            # Conversations today
            cursor.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            conversations_today = cursor.fetchone()[0]
            
            # Popular topics (you can enhance this based on message content analysis)
            cursor.execute('''
                SELECT user_message, COUNT(*) as count 
                FROM conversations 
                GROUP BY user_message 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            popular_messages = cursor.fetchall()
            
            return jsonify({
                'total_conversations': total_conversations,
                'total_leads': total_leads,
                'conversations_today': conversations_today,
                'popular_messages': [
                    {'message': msg[0], 'count': msg[1]} 
                    for msg in popular_messages
                ],
                'conversion_rate': (total_leads / total_conversations * 100) if total_conversations > 0 else 0
            })
    
    def run(self, host='localhost', port=5000, debug=False):
        """Run the chatbot server"""
        self.logger.info(f"Starting chatbot server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# HTML template for the chatbot interface
CHATBOT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Chatbot</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }
        .chat-container { 
            max-width: 600px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            overflow: hidden; 
        }
        .chat-header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 20px; 
            text-align: center; 
        }
        .chat-messages { 
            height: 400px; 
            overflow-y: auto; 
            padding: 20px; 
            background-color: #fafafa; 
        }
        .message { 
            margin: 10px 0; 
            padding: 10px 15px; 
            border-radius: 20px; 
            max-width: 80%; 
            word-wrap: break-word; 
        }
        .user-message { 
            background-color: #007bff; 
            color: white; 
            margin-left: auto; 
            text-align: right; 
        }
        .bot-message { 
            background-color: #e9ecef; 
            color: #333; 
        }
        .chat-input-container { 
            padding: 20px; 
            background-color: white; 
            border-top: 1px solid #eee; 
        }
        .chat-input { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 25px; 
            outline: none; 
            font-size: 14px; 
        }
        .chat-input:focus { 
            border-color: #007bff; 
        }
        .send-btn { 
            background-color: #007bff; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 20px; 
            cursor: pointer; 
            margin-top: 10px; 
            float: right; 
        }
        .send-btn:hover { 
            background-color: #0056b3; 
        }
        .typing-indicator { 
            display: none; 
            color: #666; 
            font-style: italic; 
            padding: 10px 15px; 
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>💬 AI Assistant</h2>
            <p>How can I help you today?</p>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                Hello! I'm here to help you. Feel free to ask me about our services or any questions you might have.
            </div>
        </div>
        <div class="typing-indicator" id="typingIndicator">Bot is typing...</div>
        <div class="chat-input-container">
            <input type="text" class="chat-input" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';
            
            // Show typing indicator
            document.getElementById('typingIndicator').style.display = 'block';
            scrollToBottom();
            
            // Send to backend
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('typingIndicator').style.display = 'none';
                addMessage(data.response, 'bot');
            })
            .catch(error => {
                document.getElementById('typingIndicator').style.display = 'none';
                addMessage('Sorry, something went wrong. Please try again.', 'bot');
                console.error('Error:', error);
            });
        }
        
        function addMessage(text, sender) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            scrollToBottom();
        }
        
        function scrollToBottom() {
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    </script>
</body>
</html>
"""

def main():
    # Create sample configuration
    sample_config = {
        "api_key": "",  # Add your OpenAI API key here
        "model": "gpt-3.5-turbo",
        "company_name": "Tech Solutions Inc",
        "business_hours": "9 AM - 6 PM IST",
        "contact_email": "info@techsolutions.com",
        "phone": "+91-9876543210",
        "website": "https://techsolutions.com",
        "services": ["Web Development", "Mobile Apps", "AI Solutions", "Digital Marketing"],
        "greeting_message": "Hello! Welcome to Tech Solutions Inc.",
        "fallback_message": "I'm sorry, I didn't understand that. Could you please rephrase your question?",
        "lead_collection": True,
        "analytics": True
    }
    
    # Save sample config
    with open('chatbot_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    # Initialize and run chatbot
    chatbot = AIWorkflowChatbot()
    print("Chatbot initialized successfully!")
    print("Available endpoints:")
    print("- http://localhost:5000/ (Chat interface)")
    print("- http://localhost:5000/leads (Leads data)")
    print("- http://localhost:5000/analytics (Analytics)")
    
    chatbot.run(debug=True)

if __name__ == "__main__":
    main()
