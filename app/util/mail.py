import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MailSender:
    def __init__(self):
        """Initialize SMTP connection using SSL and login with credentials from settings."""
        try:
            self.smtp = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
            self.smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            logger.info("Connected to SMTP server successfully.")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error during connection or login: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during SMTP connection: {e}")
            raise

    def _create_mail(self, subject, body, to, attachments=None):
        """
        Create an email message with optional attachments.

        Attr:
            subject: Email subject.
            body: Email body.
            to: Recipient email address or list of addresses.
            attachments: Optional list of file paths to attach.
        Returns:
            str: Email message as a string.
        """
        if isinstance(to, str):
            recipients = [to]
        else:
            recipients = to

        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        if attachments:
            for attachment in attachments:
                try:
                    with open(attachment, 'rb') as f:
                        part = MIMEApplication(f.read())
                    part.add_header('Content-Disposition', 'attachment', filename=attachment)
                    msg.attach(part)
                    logger.info(f"Attached file: {attachment}")
                except FileNotFoundError:
                    logger.error(f"Attachment file not found: {attachment}")
                except Exception as e:
                    logger.error(f"Error attaching file {attachment}: {e}")

        return msg.as_string()

    def send_mail(self, subject, body, to, attachments=None):
        """
        Send an email with error handling.
        
        Attr:
            subject: Email subject.
            body: Email body.
            to: Recipient email address or list of addresses.
            attachments: Optional list of file paths to attach.
        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        try:
            mail = self._create_mail(subject, body, to, attachments)
            # Allow for multiple recipients
            recipients = to if isinstance(to, list) else [to]
            self.smtp.sendmail(settings.SMTP_USER, recipients, mail)
            logger.info(f"Email sent successfully to: {recipients}")
            return True
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"All recipients were refused: {e}")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication error: {e}")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
        return False

    def __del__(self):
        """Ensure the SMTP connection is closed when the object is deleted."""
        try:
            if self.smtp:
                self.smtp.quit()
                logger.info("SMTP connection closed.")
        except Exception as e:
            logger.error(f"Error closing SMTP connection: {e}")
