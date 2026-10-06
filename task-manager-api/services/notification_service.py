import smtplib

from config.settings import settings
from utils.helpers import utc_now


class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = settings.smtp_host
        self.email_port = settings.smtp_port
        self.email_user = settings.smtp_user
        self.email_password = settings.smtp_password

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password:
            return False
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            return True
        except Exception:
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            "type": "task_assigned",
            "user_id": user.id,
            "task_id": task.id,
            "timestamp": utc_now(),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [item for item in self.notifications if item["user_id"] == user_id]
