import uuid
from datetime import datetime, timezone

class EmailService:
    def __init__(self):
        self.sent_emails = []  # Store sent emails for logging

    def send_email(self, to_email: str, subject: str, body: str, email_type: str = "notification"):
        """Mock email sending - logs email instead of actually sending"""
        email_log = {
            "id": str(uuid.uuid4()),
            "to": to_email,
            "subject": subject,
            "body": body,
            "type": email_type,
            "sent_at": datetime.now(timezone.utc),
            "status": "sent"
        }
        self.sent_emails.append(email_log)

        # Log to console for development
        print(f"\n📧 MOCK EMAIL SENT:")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print(f"Type: {email_type}")
        print(f"Sent at: {email_log['sent_at']}")
        print("=" * 50)

        return email_log

    def get_email_templates(self):
        return {
            "account_deleted": {
                "subject": "Your Finance Tracker Account Has Been Deleted",
                "body": """Dear {user_name},

We're writing to inform you that your Finance Tracker account ({user_email}) has been deleted by an administrator.

If you believe this was done in error, please contact our support team immediately.

Account Details:
- Email: {user_email}
- Deletion Date: {action_date}
- Reason: Administrative action

All your account data, including transactions and financial information, has been permanently removed from our system.

Best regards,
Finance Tracker Admin Team"""
            },
            "account_locked": {
                "subject": "Your Finance Tracker Account Has Been Locked",
                "body": """Dear {user_name},

Your Finance Tracker account ({user_email}) has been temporarily locked by an administrator.

Account Details:
- Email: {user_email}
- Lock Date: {action_date}
- Status: Locked

You will not be able to access your account until it is unlocked. If you need assistance, please contact our support team.

Best regards,
Finance Tracker Admin Team"""
            },
            "account_unlocked": {
                "subject": "Your Finance Tracker Account Has Been Unlocked",
                "body": """Dear {user_name},

Good news! Your Finance Tracker account ({user_email}) has been unlocked by an administrator.

Account Details:
- Email: {user_email}
- Unlock Date: {action_date}
- Status: Active

You can now log in and access your account normally.

Best regards,
Finance Tracker Admin Team"""
            },
            "admin_welcome": {
                "subject": "Welcome to Finance Tracker Admin Panel",
                "body": """Dear {user_name},

Congratulations! You have been granted administrator access to the Finance Tracker system.

Admin Account Details:
- Email: {user_email}
- Access Level: Administrator
- Granted Date: {action_date}

As an administrator, you can:
- View all user accounts
- Lock/unlock user accounts
- Delete user accounts
- View system statistics
- Monitor user activities

Please use these privileges responsibly and in accordance with our policies.

Best regards,
Finance Tracker System"""
            }
        }

# Global email service instance
email_service = EmailService()