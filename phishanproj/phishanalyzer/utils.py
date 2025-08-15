import random
import re
import smtplib

from bs4 import BeautifulSoup
from hashlib import sha256
from email.message import EmailMessage
from phishanalyzer.models import Link, Attachment, Email
from email.mime.text import MIMEText

LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Generates a string of letters
def generate_string(length):
    out_string = ''
    for i in range(length):
        out_string += random.choice(list(LETTERS))
    return out_string

# Transforms a file into a sha-256 hash
def get_file_hash(file):
    sha256_hash = sha256()

    for chunk in iter(lambda: file.read(4096), b""):
        sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


def get_string_hash(string):
    encoded_string = string.encode('utf-8')
    sha256_hash = sha256()
    sha256_hash.update(encoded_string)

    return sha256_hash.hexdigest()

def is_valid_url(url):
    if url[-1] == '.':
        return False
    elif url.split('.')[-1] == 'png':
        return False

    return True

def get_links_from_email(msg):
    links = set()

    for part in msg.walk():
        if part.get_content_type() in ['text/plain', 'text/html']:
            payload = part.get_payload(decode=True)

            if not payload:
                continue
            text = payload.decode(errors="ignore")

            # if part.get_content_type() == 'text/html':
            #     soup = BeautifulSoup(text, 'html.parser')
            #     for a in soup.find_all('a', href=True):
            #         links.add(a['href'])
            #     text = soup.get_text()

            pattern = r'(?:https?:\/\/|www\.)[^\s<>"]+'
            found = re.findall(pattern, text)
            for url in found:
                if is_valid_url(url):
                    print(url)
                    links.add(url)

    return list(links)


def reply_to_email(original_email, my_email, my_password, analisys_id):
    f_links = Link.objects.filter(email=analisys_id)
    f_attachments = Attachment.objects.filter(email=analisys_id)
    sid = Email.objects.get(id=analisys_id).analys_sid
    risk_score = Email.objects.get(id=analisys_id).risk_score
    msg = EmailMessage()
    msg["Subject"] = "Re: " + original_email["subject"].replace("\n", " ").replace("\r", " ").strip()
    msg["From"] = my_email
    msg["To"] = original_email["from"].replace("\n", "").replace("\r", "").strip()
    msg["In-Reply-To"] = original_email["message-id"].strip() if original_email.get("message-id") else None
    msg["References"] = original_email["message-id"].strip() if original_email.get("message-id") else None
#     msg.set_content(
#         f'''<html><body><h2>Thank you for your submission</h2>
#         <h3>Email analysis result:</h3>
#         <p>Analysis sid: {sid}</p>
#         <p>Risk score: {hash_file}</p>
#         <h3>Found links:</h3>
#         {found_links}
#         <h3>Found attachments:</h3>
#         {found_attachments}</body></html>
# '''
#     )

    found_links_block = ''
    found_attachments_block = ''
    
    if f_links:
        found_links_block = '<h3>Found links:</h3>'
        for link in f_links:
            found_links_block += f'<p>{link.hash_sha256}</p>'
            found_links_block += get_risk_score_line(link.risk_score)

    if f_attachments:
        found_attachments_block = '<h3>Found attachments:</h3>'
        for attachment in f_attachments:
            found_attachments_block += f'<p>{attachment.hash}</p>'
            found_attachments_block += get_risk_score_line(attachment.risk_score)

    html = f'''
<html><body>
<h2>Thank you for your submission</h2>
<h3>Email analysis result:</h3>
<p>Analysis sid: {sid}</p>
{get_risk_score_line(risk_score)}
{found_links_block}
{found_attachments_block}
<p style="color:grey">All links have been hidden to avoid antispam systems.</p>
</body></html>
'''

    msg.set_content("This is an HTML email. Please view in an HTML-compatible client.")
    msg.add_alternative(html, subtype='html')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(my_email, my_password)
        smtp.send_message(msg)

def get_risk_score_line(risk_score):
    if risk_score == 0:
        return f'<p>Risk score: {risk_score} | <a style="color:green">Safe</a></p>'
    elif risk_score < 5:
        return f'<p>Risk score: {risk_score} | <a style="color:yellow">Suspicious</a></p>'
    else:
        return f'<p>Risk score: {risk_score} | <a style="color:red">Dangerous</a></p>'
