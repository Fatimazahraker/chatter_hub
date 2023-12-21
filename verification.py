from email.message import EmailMessage
import os
import smtplib
import ssl

def sendmail(subject, html_email, email_receiver):
        email_sender = os.environ.get('DB_EMAIL', 'default_email')
        email_password = os.environ.get('DB_EMAIL_PASSWD', 'default_email_passwd')

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.add_alternative(html_email, subtype='html')


        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(em)