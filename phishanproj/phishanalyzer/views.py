from django.shortcuts import render, redirect
from django.http import HttpResponse

from phishanalyzer.utils import generate_string, get_file_hash
from phishanalyzer.models import Email, Link, Attachment
from phishanalyzer.email_parser import analyze_email
from phishanalyzer.virustotal import send_url_vt, send_file_vt
from phishanalyzer.tasks import analyze_email_vt, checkmailbox


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

            new_email_obj.author.set([request.user])

            analyze_email(uploaded_file, new_email_obj)

            analyze_email_vt.delay(new_email_obj.id)

        return redirect('detailedpage', new_email_obj.analys_sid)
    
    return render(request, 'phishanalyzer/index.html')

def detailpage(request, analys_sid):
    email_obj = Email.objects.get(analys_sid=analys_sid)
    context = {
        'analisys_id':analys_sid,
        'status':email_obj.status,
        'risk_score':email_obj.risk_score,
        'hash':email_obj.hash_sha256,
        'urls':Link.objects.filter(email=email_obj),
        'attachments':Attachment.objects.filter(email=email_obj)
    }
    # checkmailbox.delay()
    return render(request, 'phishanalyzer/detailpage.html', context)

def guidepage(request):
    return render(request, 'phishanalyzer/guide.html')

def searchpage(request):
    if request.GET.get('sid'):
        return redirect('detailedpage', request.GET.get('sid'))

    return render(request, 'phishanalyzer/search.html')