from django.urls import path

from phishanalyzer.views import mainpage

urlpatterns = [
    path('', mainpage),
]