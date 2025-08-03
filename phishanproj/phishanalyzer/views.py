from django.shortcuts import render
from django.http import HttpResponse

from phishanalyzer.utils import generate_string, get_file_hash
from phishanalyzer.models import Email, Link, Attachment
from phishanalyzer.email_parser import analyze_email
from phishanalyzer.virustotal import send_url_vt, send_file_vt


def mainpage(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('email')

        if str(uploaded_file).split('.')[-1] != 'eml':
            return HttpResponse('Файл має бути у форматі .eml')

        with uploaded_file.open() as new_email:
            new_email_sid = generate_string(30)
            new_email_hash_sha256 = get_file_hash(new_email)

            new_email_obj = Email(analys_sid=new_email_sid, hash_sha256=new_email_hash_sha256, file=new_email)
            new_email_obj.save()

            analyze_email(uploaded_file, new_email_obj)

            got_urls = Link.objects.all().filter(email=new_email_obj)
            got_attachments = Attachment.objects.all().filter(email=new_email_obj)

            for link in got_urls:
                res = send_url_vt(link.url)
                risk_score = res.get('malicious') + res.get('suspicious')//2
                link.status = 'FN'
                link.risk_score = risk_score
                link.save()

            for attachment in got_attachments:
                res = send_file_vt(attachment.file)
                risk_score = res.get('malicious') + res.get('suspicious')//2
                attachment.status = 'FN'
                attachment.risk_score = risk_score
                attachment.save()

        return render(request, 'phishanalyzer/index.html')
    
    return render(request, 'phishanalyzer/index.html')