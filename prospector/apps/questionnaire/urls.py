from django.urls import path

from . import views

app_name = "questionnaire"

urlpatterns = [
    path("", views.Start.as_view(), name="start"),
    path("name", views.RespondentName.as_view(), name="respondent-name"),
    path("role", views.RespondentRole.as_view(), name="respondent-role"),
    path(
        "relationship",
        views.RespondentRelationship.as_view(),
        name="respondent-relationship",
    ),
]
