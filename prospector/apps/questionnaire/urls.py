from django.urls import path

from . import views

app_name = "questionnaire"

urlpatterns = [
    path("", views.Start.as_view(), name="start"),
    path("name", views.RespondentName.as_view(), name="respondent-name"),
]
