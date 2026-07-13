import os
import json
import logging
from datetime import datetime

# Setup a local logging format to mock email deliveries
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotificationService")

class BaseEmailProvider:
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        raise NotImplementedError("Email providers must implement send_email")

class ConsoleEmailProvider(BaseEmailProvider):
    """
    Standard provider that logs emails to console and logs folder.
    This is highly useful for local debugging and is production-ready for offline/staging mode.
    """
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "dispatched_emails.log")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "to": to_email,
            "subject": subject,
            "body": html_content
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
        logger.info(f"Dispatched email to {to_email} with subject: '{subject}' (Logged to {log_file})")
        return True

# SMTP or SendGrid provider placeholder templates (ready to plug in)
class SMTPEmailProvider(BaseEmailProvider):
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        # Future SMTP send logic using smtplib
        return True

class SendGridEmailProvider(BaseEmailProvider):
    def __init__(self, api_key):
        self.api_key = api_key

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        # Future SendGrid SDK send logic
        return True


class NotificationService:
    def __init__(self, provider: BaseEmailProvider = None):
        self.provider = provider or ConsoleEmailProvider()

    def send_analysis_complete_email(self, to_email: str, filename: str, score: float, sci_score: float) -> bool:
        subject = f"GreenDev AI — Code Analysis Completed: {filename}"
        html_content = f"""
        <html>
        <body>
            <h2>Analysis Completed successfully!</h2>
            <p>Your Python file <strong>{filename}</strong> has been analysed by the GreenDev AI multi-agent pipeline.</p>
            <ul>
                <li><strong>Green Score:</strong> {score}/10</li>
                <li><strong>Estimated SCI:</strong> {sci_score:.4f} gCO2eq/run</li>
            </ul>
            <p>Open your dashboard to download the complete report and apply code-level energy recommendations.</p>
            <br>
            <p>Best regards,<br>The GreenDev AI Team</p>
        </body>
        </html>
        """
        return self.provider.send_email(to_email, subject, html_content)

    def send_weekly_digest(self, to_email: str, total_runs: int, co2_saved: str) -> bool:
        subject = "GreenDev AI — Weekly Carbon Digest"
        html_content = f"""
        <html>
        <body>
            <h2>Weekly Carbon Summary</h2>
            <p>Here is your green software metrics digest for the past week:</p>
            <ul>
                <li><strong>Analyses Run:</strong> {total_runs}</li>
                <li><strong>Carbon Emissions Avoided:</strong> {co2_saved}</li>
            </ul>
            <p>Keep optimizing your code structure to save more computing energy!</p>
            <br>
            <p>Best regards,<br>The GreenDev AI Team</p>
        </body>
        </html>
        """
        return self.provider.send_email(to_email, subject, html_content)

    def send_security_notification(self, to_email: str, alert_type: str, details: str) -> bool:
        subject = f"GreenDev AI — Security Alert: {alert_type}"
        html_content = f"""
        <html>
        <body>
            <h2>Security Notification</h2>
            <p>We detected an event on your account: <strong>{alert_type}</strong></p>
            <p>Details: {details}</p>
            <br>
            <p>If this wasn't you, please change your password or revoke your active API keys.</p>
        </body>
        </html>
        """
        return self.provider.send_email(to_email, subject, html_content)

# Global singleton instantiation
notification_service = NotificationService()
