from django.shortcuts import render
from django.http import HttpResponse

from phishanalyzer.utils import generate_string, get_file_hash
from phishanalyzer.models import Email
from phishanalyzer.email_parser import analyze_email


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

        return render(request, 'phishanalyzer/index.html')
    
    return render(request, 'phishanalyzer/index.html')