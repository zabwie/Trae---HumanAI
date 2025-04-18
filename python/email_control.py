import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import os
import re
from typing import List, Dict, Optional
import logging

class EmailController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.smtp_server = None
        self.imap_server = None
        self.email = None
        self.password = None
        self.connected = False
        
    def connect(self, email: str, password: str, smtp_server: str = "smtp.gmail.com", 
                smtp_port: int = 587, imap_server: str = "imap.gmail.com", 
                imap_port: int = 993) -> bool:
        """Connect to email servers"""
        try:
            # Store credentials
            self.email = email
            self.password = password
            
            # Connect to SMTP server
            self.smtp_server = smtplib.SMTP(smtp_server, smtp_port)
            self.smtp_server.starttls()
            self.smtp_server.login(email, password)
            
            # Connect to IMAP server
            self.imap_server = imaplib.IMAP4_SSL(imap_server, imap_port)
            self.imap_server.login(email, password)
            
            self.connected = True
            self.logger.info("Successfully connected to email servers")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to email servers: {str(e)}")
            self.connected = False
            return False
            
    def disconnect(self) -> None:
        """Disconnect from email servers"""
        try:
            if self.smtp_server:
                self.smtp_server.quit()
            if self.imap_server:
                self.imap_server.logout()
            self.connected = False
            self.logger.info("Disconnected from email servers")
        except Exception as e:
            self.logger.error(f"Error disconnecting from email servers: {str(e)}")
            
    def send_email(self, to_email: str, subject: str, body: str, 
                  attachments: List[str] = None) -> bool:
        """Send an email with optional attachments"""
        if not self.connected:
            self.logger.error("Not connected to email servers")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            attachment = MIMEText(f.read())
                            attachment.add_header('Content-Disposition', 
                                               'attachment', 
                                               filename=os.path.basename(file_path))
                            msg.attach(attachment)
                            
            # Send email
            self.smtp_server.send_message(msg)
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
            
    def get_emails(self, folder: str = "INBOX", limit: int = 10, 
                  unread_only: bool = False) -> List[Dict]:
        """Get emails from specified folder"""
        if not self.connected:
            self.logger.error("Not connected to email servers")
            return []
            
        try:
            # Select folder
            self.imap_server.select(folder)
            
            # Search criteria
            search_criteria = '(UNSEEN)' if unread_only else 'ALL'
            
            # Search for emails
            _, message_numbers = self.imap_server.search(None, search_criteria)
            
            emails = []
            for num in message_numbers[0].split()[:limit]:
                _, msg_data = self.imap_server.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Get email details
                subject = self._decode_header(email_message['Subject'])
                from_addr = self._decode_header(email_message['From'])
                date = email_message['Date']
                
                # Get email body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = email_message.get_payload(decode=True).decode()
                    
                emails.append({
                    'subject': subject,
                    'from': from_addr,
                    'date': date,
                    'body': body
                })
                
            return emails
            
        except Exception as e:
            self.logger.error(f"Error getting emails: {str(e)}")
            return []
            
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        try:
            decoded_chunks = decode_header(header)
            decoded_header = ""
            for chunk, encoding in decoded_chunks:
                if isinstance(chunk, bytes):
                    if encoding:
                        decoded_header += chunk.decode(encoding)
                    else:
                        decoded_header += chunk.decode()
                else:
                    decoded_header += chunk
            return decoded_header
        except:
            return header
            
    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read"""
        if not self.connected:
            self.logger.error("Not connected to email servers")
            return False
            
        try:
            self.imap_server.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            self.logger.error(f"Error marking email as read: {str(e)}")
            return False
            
    def delete_email(self, email_id: str) -> bool:
        """Delete an email"""
        if not self.connected:
            self.logger.error("Not connected to email servers")
            return False
            
        try:
            self.imap_server.store(email_id, '+FLAGS', '\\Deleted')
            self.imap_server.expunge()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting email: {str(e)}")
            return False 