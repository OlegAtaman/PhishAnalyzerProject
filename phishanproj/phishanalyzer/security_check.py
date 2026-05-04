import os
from django.conf import settings
from django.core.cache import cache
from phishanalyzer.models import Attachment, Email

def count_analysis_attempt(user_ip):
    global_analyses = cache.get(f"global_analyses", 0)
    ip_analyses = cache.get(f"analyses_ip:{user_ip}", 0)

    if ip_analyses > 2 or global_analyses > 4:
        return False, "Too intence load on server. Please try later."
    
    cache.set(f"global_analyses", global_analyses + 1, timeout=300)
    cache.set(f"analyses_ip:{user_ip}", ip_analyses + 1, timeout=300)
    return True, "Success."

def is_orphan_file(file_path):
    if not file_path:
        return True

    try:
        relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
    except ValueError:
        return True

    # print("ABS:", file_path)
    # print("REL:", relative_path)

    relative_path = relative_path.replace("\\", "/")

    exists_in_email = Email.objects.filter(file=relative_path).exists()
    exists_in_attachment = Attachment.objects.filter(file=relative_path).exists()

    return not (exists_in_email or exists_in_attachment)