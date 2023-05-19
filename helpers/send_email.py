from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
from jinja2 import Template

def send_email(recipient_email, recs):
    sender_email = "universalstreamsearch@gmail.com"
    sender_password = "irbupoljuvsimpbu"
    
    with open('templates/email-template.html', 'r') as f:
        template = Template(f.read())
    
    context = {
        'subject': 'Your recommendations from Universal Stream Search',
        'recs': recs
    }

    html = template.render(context)

    msg = MIMEMultipart('alternative')
    msg['From']    = sender_email
    msg['Subject'] = 'Your recommendations from Universal Stream Search'
    msg['To']      = recipient_email
    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()
