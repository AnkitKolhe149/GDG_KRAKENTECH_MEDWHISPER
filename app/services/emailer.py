"""Simple SMTP email helper using app config.

Required config keys in Flask `current_app.config`:
- MAIL_SERVER
- MAIL_PORT
- MAIL_USERNAME
- MAIL_PASSWORD
- MAIL_USE_TLS (bool)
- MAIL_FROM (optional, defaults to MAIL_USERNAME)
"""
import smtplib
from email.message import EmailMessage
from flask import current_app
import logging

logger = logging.getLogger(__name__)


def send_email(subject: str, html_body: str, to_email: str) -> bool:
    cfg = current_app.config
    mail_server = cfg.get('MAIL_SERVER')
    mail_port = cfg.get('MAIL_PORT')
    mail_user = cfg.get('MAIL_USERNAME')
    mail_pass = cfg.get('MAIL_PASSWORD')
    mail_use_tls = cfg.get('MAIL_USE_TLS', True)
    mail_from = cfg.get('MAIL_FROM') or mail_user

    if not (mail_server and mail_port and mail_user and mail_pass):
        logger.error('SMTP configuration missing')
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = mail_from
        msg['To'] = to_email
        msg.set_content('This is an HTML email. Enable HTML view to see content.')
        msg.add_alternative(html_body, subtype='html')

        if mail_use_tls:
            server = smtplib.SMTP(mail_server, mail_port, timeout=20)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=20)

        server.login(mail_user, mail_pass)
        server.send_message(msg)
        server.quit()
        logger.info(f'Email sent to {to_email}')
        return True
    except Exception as e:
        logger.error(f'Failed to send email: {e}')
        return False
