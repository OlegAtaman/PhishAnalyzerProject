from django.urls import path

from phishanalyzer.views import mainpage, detailpage

urlpatterns = [
    path('', mainpage, name='mainpage'),
    path('analysis/<analys_sid>', detailpage, name='detailedpage')
]