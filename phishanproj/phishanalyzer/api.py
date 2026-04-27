from django.http import JsonResponse

from phishanalyzer.models import Email


def analysis_poll(request, analysis_sid):
    analysis_obj = Email.objects.get(analys_sid=analysis_sid)
    print(analysis_obj)

    analysis_status = {
        'status':analysis_obj.status,
        'score':analysis_obj.risk_score
        }

    link_statuses = {}
    attachment_statuses = {}

    for link in analysis_obj.link_set.all():
        stats = {'status':link.status, 'score':link.risk_score}
        link_statuses.update({link.id:stats})

    for att in analysis_obj.attachment_set.all():
        stats = {'status':att.status, 'score':att.risk_score}
        attachment_statuses.update({att.id:stats})

    final_dict = {
        'analysis_status':analysis_status,
        'link_statuses':link_statuses,
        'attachment_statuses':attachment_statuses
    }

    return JsonResponse(final_dict)