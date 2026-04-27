import imaplib, os

from dotenv import load_dotenv
from celery import shared_task

from phishanalyzer.models import Email
from phishanalyzer.virustotal import send_url_vt, send_file_vt, get_url_vt
from phishanalyzer.utils import reply_to_email
from phishanalyzer.email_parser import analyze_email
from phishanalyzer.imap_parcer import scrap_mailbox


load_dotenv()

GMAIL_USERNAME = 'test.phish.analyzer@gmail.com'
GMAIL_PASS = os.getenv('GOOGLEE_APP_PASSWORD')

@shared_task
def analyze_email_vt(email_id):
    email_obj = Email.objects.get(id=email_id)

    for link in email_obj.link_set.all():
        link.analysis_id = send_url_vt(link.url)
        link.status = 'AN'
        link.save()

    for att in email_obj.attachment_set.all():
        att.analysis_id = send_file_vt(att.file)
        att.status = 'AN'
        att.save()

    poll_results.delay(email_id)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, max_retries=5)
def poll_results(self, email_id):
    email_obj = Email.objects.get(id=email_id)
    all_done = True

    for link in email_obj.link_set.all():
        if link.status != 'FN':
            results = get_url_vt(link.analysis_id)

            if not results:
                all_done = False
                continue

            link.risk_score = results.get('malicious') + results.get('suspicious')//2
            link.status = 'FN'
            link.save()

    for att in email_obj.attachment_set.all():
        if att.status != 'FN':
            results = get_url_vt(att.analysis_id)

            if not results:
                all_done = False
                continue

            att.risk_score = results.get('malicious') + results.get('suspicious')//2
            att.status = 'FN'
            att.file.delete(save=False)
            att.save()

    if not all_done:
        raise self.retry()
    finalize_email.delay(email_id)

@shared_task
def finalize_email(email_id):
    email_obj = Email.objects.get(id=email_id)

    max_score = max(
        [l.risk_score for l in email_obj.link_set.all()] +
        [a.risk_score for a in email_obj.attachment_set.all()],
        default=0
    )

    email_obj.risk_score = max_score
    email_obj.status = 'FN'
    email_obj.file.delete(save=False)
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