from celery import chain
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden

from phishanalyzer.utils import generate_string, get_file_hash
from phishanalyzer.models import Email, Link, Attachment
from phishanalyzer.email_parser import analyze_email
from phishanalyzer.tasks import analyze_email_vt, finalize_email, poll_results
from authapp.utils import get_client_ip
from phishanalyzer.security_check import count_analysis_attempt
from django.contrib import messages


def mainpage(request):
    if request.method == 'POST':
        user_ip = get_client_ip(request)
        alowance, exp = count_analysis_attempt(user_ip)
        if not alowance:
            messages.error(request, exp)
            return redirect('mainpage')
        uploaded_file = request.FILES.get('email')

        if str(uploaded_file).split('.')[-1] != 'eml':
            return HttpResponse('Файл має бути у форматі .eml')

        with uploaded_file.open() as new_email:
            new_email_sid = generate_string(30)
            new_email_hash_sha256 = get_file_hash(new_email)

            new_email_obj = Email(analys_sid=new_email_sid, hash_sha256=new_email_hash_sha256)
            new_email_obj.save()

            if request.user.is_authenticated:
                new_email_obj.author.set([request.user])

            analyze_email(uploaded_file, new_email_obj)

            chain(analyze_email_vt.s(), poll_results.s(), finalize_email.s(),).delay(new_email_obj.id)

        return redirect('detailedpage', new_email_obj.analys_sid)
    
    return render(request, 'phishanalyzer/index.html')

def detailpage(request, analys_sid):
    email_obj = Email.objects.get(analys_sid=analys_sid)
    context = {
        'analisys_id':analys_sid,
        'status':email_obj.status,
        'uploaded_at':email_obj.uploaded_at,
        'risk_score':email_obj.risk_score,
        'hash':email_obj.hash_sha256,
        'urls':Link.objects.filter(email=email_obj),
        'attachments':Attachment.objects.filter(email=email_obj),
        'from':email_obj.email_from,
        'to':email_obj.email_to,
        'subj':email_obj.email_subject
    }
    # checkmailbox.delay()
    return render(request, 'phishanalyzer/detailpage.html', context)

def guidepage(request):
    return render(request, 'phishanalyzer/guide.html')

def searchpage(request):
    if not request.GET.get('sid'):
        return render(request, 'phishanalyzer/search.html')

    email_obj = Email.objects.filter(analys_sid=request.GET.get('sid')).first()

    if not email_obj:
        messages.error(request, 'Analysis does not exist or you do not have access to it')
        return redirect('searchpage')
    if email_obj.author.all() and email_obj.author.all().first() != request.user:
        messages.error(request, 'Analysis does not exist or you do not have access to it')
        return redirect('searchpage')
    return redirect('detailedpage', request.GET.get('sid'))

def deletepage(request, analysis_sid):
    if request.method != 'POST':
        return HttpResponseForbidden("The page can ot be reached")
    
    analysis_obj = Email.objects.filter(analys_sid=analysis_sid).first()
    if not analysis_obj:
        return HttpResponseForbidden("The page can ot be reached")
    
    if request.user in analysis_obj.author.all() and request.user.is_authenticated:
        analysis_obj.delete()
        return redirect('profile_user', request.user.username)
        
    return HttpResponseForbidden("The page can ot be reached")