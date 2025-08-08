from celery import shared_task

from phishanalyzer.models import Link, Attachment, Email
from phishanalyzer.virustotal import send_url_vt, send_file_vt, get_url_vt, get_file_vt


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