import smtplib

from email.message import EmailMessage


def send_code(email, code, my_email, my_password, completed_url):
    msg = EmailMessage()

    msg["Subject"] = "Fishanalyzer registration: confirm your email"
    msg["From"] = my_email
    msg["To"] = email
    


    html = f'''
<html><body>
<h2>Welcome to Fishanalyzer!</h2>
<h3>To continue registration, enter the code: <b>{code}</b></h3>
<h3>Url to registration page: {completed_url}</h3>
<h3>Please, finish your registration in 15 minutes or the code will expire.</h3>
</body></html>
'''

    msg.set_content("This is an HTML email. Please view in an HTML-compatible client.")
    msg.add_alternative(html, subtype='html')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(my_email, my_password)
        smtp.send_message(msg)
