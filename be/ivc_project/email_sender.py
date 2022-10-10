import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ivc_project.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_HOST, EMAIL_PORT


def send_new_email(email_subject, email_content, destination_email):
    """
    Sends an email from our website email (which is set inside settings.py at the end)
    to destination_email given as a parameter


    """
    message = MIMEMultipart()
    message["From"] = EMAIL_HOST_USER
    message["To"] = destination_email

    message["Subject"] = email_subject
    content = email_content

    # Add body to email
    message.attach(MIMEText(content, "plain"))
    text = message.as_string()
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(EMAIL_HOST, 465, context=context) as server:
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER,
                        destination_email,
                        text)
