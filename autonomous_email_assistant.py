import email
import imaplib
import os
import smtplib
from email.message import EmailMessage


class AutonomousEmailAssistant:
    def __init__(self):
        # Default configuration, expected to be set by the user or .env
        self.email_address = os.getenv("EMAIL_ADDRESS", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", 993))
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.is_configured = bool(self.email_address and self.email_password)

    def check_unread_emails(self, limit=5):
        if not self.is_configured:
            return "Email is not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in your environment variables."

        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            mail.select("inbox")

            status, messages = mail.search(None, "UNSEEN")
            if status != "OK":
                return "Failed to search for unread emails."

            mail_ids = messages[0].split()
            if not mail_ids:
                return "No new unread emails."

            mail_ids = mail_ids[-limit:]  # Get the latest N emails

            results = []
            for mail_id in mail_ids:
                status, data = mail.fetch(mail_id, "(RFC822)")
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg["subject"]
                        sender = msg["from"]
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body += part.get_payload(decode=True).decode()
                        else:
                            body = msg.get_payload(decode=True).decode()

                        results.append(
                            {
                                "sender": sender,
                                "subject": subject,
                                "snippet": (
                                    body[:200] + "..." if len(body) > 200 else body
                                ),
                            }
                        )
            mail.logout()
            return f"Found {len(results)} unread emails:\n" + "\n".join(
                [
                    f"- From: {r['sender']}\n  Subject: {r['subject']}\n  Snippet: {r['snippet']}"
                    for r in results
                ]
            )
        except Exception as e:
            return f"Error checking emails: {e}"

    def send_email(self, to_address, subject, body):
        if not self.is_configured:
            return (
                "Email is not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD."
            )

        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = self.email_address
            msg["To"] = to_address

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            return f"Email successfully sent to {to_address}"
        except Exception as e:
            return f"Failed to send email: {e}"

    def process_intent(self, intent_data):
        action = intent_data.get("action", "")
        if action == "check_emails":
            return self.check_unread_emails()
        elif action == "send_email":
            to = intent_data.get("to_address", "")
            subject = intent_data.get("subject", "Automated Message from DEEP")
            body = intent_data.get("body", "")
            if to and body:
                return self.send_email(to, subject, body)
            return "Missing recipient or body for sending email."
        else:
            return "Unknown email action."


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = AutonomousEmailAssistant()
    print("Autonomous Email Engine Ready")
