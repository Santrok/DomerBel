import smtplib

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from pathlib import Path


@shared_task()
def send_email_about_message_in_chat(chat_title, recipient, text_content, html_content):
    try:
        msg = EmailMultiAlternatives(
            chat_title,
            text_content,
            None,
            [recipient],
        )
        path = Path('main_page_domer/static/img/logo.png')
        with path.open("rb") as file:
            content = MIMEImage(file.read())
            content.add_header("Content-ID", "<logo.png>")
            content.add_header("Content-Type", "image/png")
            content.add_header("Content-Disposition", "inline")
            content.add_header("Content-Transfer-Encoding", "base64")
            msg.attach(content)

        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except smtplib.SMTPException:
        pass
