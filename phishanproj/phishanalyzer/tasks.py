import imaplib, os, vt

from dotenv import load_dotenv
from celery import chain, shared_task

from phishanalyzer.models import Email
from phishanalyzer.virustotal import get_file_result_by_hash, get_result_vt, get_url_result_by_hash, send_url_vt, send_file_vt
from phishanalyzer.utils import parce_inbox_email_data, reply_to_email
from phishanalyzer.email_parser import analyze_email
from phishanalyzer.imap_parcer import scrap_mailbox
from authapp.models import ConfirmationEmail
from django.conf import settings
from phishanalyzer.security_check import is_orphan_file


load_dotenv()

GMAIL_USERNAME = 'phishanalyzer.dev@gmail.com'
GMAIL_PASS = os.getenv('GOOGLEE_APP_PASSWORD')
api_key = os.getenv('VIRUSTOTAL_API_KEY')
vt_url = 'https://www.virustotal.com/api/v3'

# @shared_task(
#     bind=True,
#     autoretry_for=(Exception,),
#     retry_backoff=True,
#     retry_jitter=True,
#     max_retries=5
# )
@shared_task
def analyze_email_vt(email_id):
    email_obj = Email.objects.get(id=email_id)
    client = vt.Client(api_key)

    try:
        for link in email_obj.link_set.all():
            old_results = get_url_result_by_hash(link.vt_url_id, client)
            if old_results:
                link.risk_score = old_results.get('malicious') + old_results.get('suspicious')//2
                link.status = 'FN'
                link.save()
            else:
                link.analysis_id = send_url_vt(link.url, client)
                link.status = 'AN'
                link.save()

        for att in email_obj.attachment_set.all():
            old_results = get_file_result_by_hash(att.hash_sha256, client)
            if old_results:
                att.risk_score = old_results.get('malicious') + old_results.get('suspicious')//2
                att.status = 'FN'
                att.file.delete(save=False)
                att.save()
            else:
                att.analysis_id = send_file_vt(att.file, client)
                att.status = 'AN'
                att.save()
    finally:
        # print('Something went wrong trying to send an analysis')
        client.close()

    return email_id

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, max_retries=5)
def poll_results(self, email_id):
    client =  vt.Client(api_key)
    email_obj = Email.objects.get(id=email_id)
    all_done = True

    try:
        for link in email_obj.link_set.all():
            if link.status != 'FN':
                results = get_result_vt(link.analysis_id, client)

                if not results:
                    all_done = False
                    continue

                link.risk_score = results.get('malicious') + results.get('suspicious')//2
                link.status = 'FN'
                link.save()

        for att in email_obj.attachment_set.all():
            if att.status != 'FN':
                results = get_result_vt(att.analysis_id, client)

                if not results:
                    all_done = False
                    continue

                att.risk_score = results.get('malicious') + results.get('suspicious')//2
                att.status = 'FN'
                att.file.delete(save=False)
                att.save()
    finally:
        # print('Something went wrong trying to get analysis result')
        client.close()

    if not all_done:
        raise self.retry()
    return email_id

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
    return email_id

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
        mail_data = parce_inbox_email_data(new_emails_to_analyze.get(email_id))
        chain(
            analyze_email_vt.s(),
            poll_results.s(),
            finalize_email.s(),
            send_analysis_reply.s(mail_data, GMAIL_USERNAME, GMAIL_PASS)
            ).delay(email_obj.id)
        # send_analysis_reply.delay(mail_data, GMAIL_USERNAME, GMAIL_PASS, email_obj.id)

    mail.close()

@shared_task
def delete_confirmation(obj_id):
    ConfirmationEmail.objects.filter(id=obj_id).delete()

@shared_task
def cleanup_files():
    folders = [
        os.path.join(settings.MEDIA_ROOT, 'attachments'),
        os.path.join(settings.MEDIA_ROOT, 'emails'),
    ]

    for folder in folders:
        if not os.path.exists(folder):
            continue

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)

            if os.path.isfile(file_path):
                # print(f"Is orphan - {is_orphan_file(file_path)}")
                if is_orphan_file(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5
)
def send_analysis_reply(analisys_id, original_email, my_email, my_password):
    reply_to_email(original_email, my_email, my_password, analisys_id)