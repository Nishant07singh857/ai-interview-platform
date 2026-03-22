"""
Email Service - Email sending functionality
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

# Jinja2 template environment
template_dir = os.path.join(os.path.dirname(__file__), '../../templates/email')
os.makedirs(template_dir, exist_ok=True)
template_env = Environment(loader=FileSystemLoader(template_dir))

class EmailSender:
    """Email sending service"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP"""
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = to_email
        
        # Add text version
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        
        # Add HTML version
        msg.attach(MIMEText(html_content, 'html'))
        
        try:
            # Send email
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_template_email(
        self,
        to_email: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> bool:
        """Send email using template"""
        
        try:
            # Load template
            template = template_env.get_template(f"{template_name}.html")
            html_content = template.render(**context)
            
            # Try to load text template if exists
            try:
                text_template = template_env.get_template(f"{template_name}.txt")
                text_content = text_template.render(**context)
            except:
                text_content = None
            
            # Get subject from context or use default
            subject = context.get('subject', f"Notification from {settings.APP_NAME}")
            
            return await self.send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            return False
    
    async def send_welcome_email(self, to_email: str, name: str):
        """Send welcome email to new user"""
        
        context = {
            'user_name': name,
            'app_name': settings.APP_NAME,
            'login_url': f"{settings.APP_URL}/login",
            'support_email': settings.EMAIL_FROM,
            'year': datetime.utcnow().year
        }
        
        await self.send_template_email(to_email, 'welcome', context)
    
    async def send_password_reset_email(self, to_email: str, name: str, reset_token: str):
        """Send password reset email"""
        
        reset_url = f"{settings.APP_URL}/reset-password?token={reset_token}"
        
        context = {
            'user_name': name,
            'reset_url': reset_url,
            'expires_in': '1 hour',
            'app_name': settings.APP_NAME,
            'support_email': settings.EMAIL_FROM,
            'year': datetime.utcnow().year
        }
        
        await self.send_template_email(to_email, 'password_reset', context)
    
    async def send_verification_email(self, to_email: str, name: str, verification_token: str):
        """Send email verification email"""
        
        verify_url = f"{settings.APP_URL}/verify-email?token={verification_token}"
        
        context = {
            'user_name': name,
            'verify_url': verify_url,
            'expires_in': '24 hours',
            'app_name': settings.APP_NAME,
            'support_email': settings.EMAIL_FROM,
            'year': datetime.utcnow().year
        }
        
        await self.send_template_email(to_email, 'email_verification', context)
    
    async def send_practice_reminder(self, to_email: str, name: str, days_inactive: int):
        """Send practice reminder email"""
        
        context = {
            'user_name': name,
            'days_inactive': days_inactive,
            'practice_url': f"{settings.APP_URL}/practice",
            'app_name': settings.APP_NAME,
            'year': datetime.utcnow().year
        }
        
        await self.send_template_email(to_email, 'practice_reminder', context)
    
    async def send_weekly_report(self, to_email: str, name: str, report_data: Dict[str, Any]):
        """Send weekly progress report email"""
        
        context = {
            'user_name': name,
            'week_start': report_data.get('week_start'),
            'week_end': report_data.get('week_end'),
            'total_questions': report_data.get('total_questions', 0),
            'accuracy': report_data.get('accuracy', 0),
            'time_spent': report_data.get('time_spent', 0),
            'streak': report_data.get('streak', 0),
            'improved_topics': report_data.get('improved_topics', []),
            'report_url': f"{settings.APP_URL}/analytics",
            'app_name': settings.APP_NAME,
            'year': datetime.utcnow().year
        }
        
        await self.send_template_email(to_email, 'weekly_report', context)

# Global instance
email_sender = EmailSender()