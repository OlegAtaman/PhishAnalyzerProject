import imaplib, os

from dotenv import load_dotenv
from celery import shared_task

from phishanalyzer.models import Link, Attachment, Email
from phishanalyzer.virustotal import send_url_vt, send_file_vt, get_url_vt
from phishanalyzer.utils import reply_to_email
from phishanalyzer.email_parser import analyze_email
from phishanalyzer.imap_parcer import scrap_mailbox


load_dotenv()

GMAIL_USERNAME = 'test.phish.analyzer@gmail.com'
GMAIL_PASS = os.getenv('GOOGLEE_APP_PASSWORD')

@shared_task
def analyze_email_vt(email_obj_id):
    email_obj = Email.objects.get(id=email_obj_id)

    urls = Link.objects.all().filter(email=email_obj)
    attachments = Attachment.objects.all().filter(email=email_obj)

    url_an_ids = {}
    attachment_an_ids = {}

    for url in urls:
        url_an_ids.update({url.id:send_url_vt(url.url)})

    for attachment in attachments:
        attachment_an_ids.update({attachment.id:send_file_vt(attachment.file)})

    max_risk_score = 0

    for url_id, analysis in url_an_ids.items():
        results = get_url_vt(analysis)
        risk_score = results.get('malicious') + results.get('suspicious')//2
        obj = Link.objects.get(id=url_id)
        obj.status = 'FN'
        obj.risk_score = risk_score
        if risk_score > max_risk_score:
            max_risk_score = risk_score
        obj.save()

    for attachment_id, analysis in attachment_an_ids.items():
        results = get_url_vt(analysis)
        risk_score = results.get('malicious') + results.get('suspicious')//2
        obj = Attachment.objects.get(id=attachment_id)
        obj.status = 'FN'
        obj.risk_score = risk_score
        if risk_score > max_risk_score:
            max_risk_score = risk_score
        obj.save()

    email_obj.status = 'FN'
    email_obj.risk_score = max_risk_score
    email_obj.save()


@shared_task
def checkmailbox():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(GMAIL_USERNAME, GMAIL_PASS)

    folders = [
        'inbox',
        "[Gmail]/Spam"
    ]

    new_emails_to_analyze = {}

    for f in folders:
        new_emails_to_analyze.update(scrap_mailbox(f, mail))

    for email_id in new_emails_to_analyze.keys():
        email_obj = Email.objects.get(id=email_id)

        analyze_email(email_obj.file, email_obj)
        analyze_email_vt(email_id)

        reply_to_email(new_emails_to_analyze.get(email_id), GMAIL_USERNAME, GMAIL_PASS, email_obj.id)


    mail.close()