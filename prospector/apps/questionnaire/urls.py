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
    path("need-permission", views.NeedPermission.as_view(), name="need-permission"),
    path("your-postcode", views.Postcode.as_view(), name="postcode"),
    path("your-address", views.RespondentAddress.as_view(), name="respondent-address"),
    path("your-email", views.Email.as_view(), name="email"),
    path("phone-number", views.ContactPhone.as_view(), name="contact-phone"),
    path("occupant-name", views.OccupantName.as_view(), name="occupant-name"),
    path("property-address", views.PropertyAddress.as_view(), name="property-address"),
    path(
        "property-ownership",
        views.PropertyOwnership.as_view(),
        name="property-ownership",
    ),
    path("consents", views.Consents.as_view(), name="consents"),
    path("epc", views.SelectEPC.as_view(), name="select-e-p-c"),
]
