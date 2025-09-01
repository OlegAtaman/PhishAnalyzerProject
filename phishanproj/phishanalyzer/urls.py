from django.urls import path

from phishanalyzer.views import mainpage, detailpage, guidepage, searchpage

urlpatterns = [
    path('', mainpage, name='mainpage'),
    path('analysis/<analys_sid>', detailpage, name='detailedpage'),
    path('guide/', guidepage, name="guidepage"),
    path('search/', searchpage, name='searchpage'),
]