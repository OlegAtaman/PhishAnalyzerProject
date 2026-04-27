from django.urls import path

from phishanalyzer.views import mainpage, detailpage, guidepage, searchpage
from phishanalyzer.api import analysis_poll

urlpatterns = [
    path('', mainpage, name='mainpage'),
    path('analysis/<analys_sid>', detailpage, name='detailedpage'),
    path('api/get-status/<analysis_sid>', analysis_poll, name='poll_analysis'),
    path('guide/', guidepage, name="guidepage"),
    path('search/', searchpage, name='searchpage'),
]