from flask_mail import Message
from app import mail

# Flask_Mail also supports additional functionality 
#       like Cc and Bcc lists 
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)