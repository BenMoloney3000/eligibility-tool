from django.urls import path

from .views import trail as views

app_name = "questionnaire"

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("start", views.Start.as_view(), name="start"),
    path("name", views.RespondentName.as_view(), name="respondent-name"),
    path("role", views.RespondentRole.as_view(), name="respondent-role"),
    path(
        "consent",
        views.RespondentHasPermission.as_view(),
        name="respondent-has-permission",
    ),
    path(
        "your-postcode", views.RespondentPostcode.as_view(), name="respondent-postcode"
    ),
    path("your-address", views.RespondentAddress.as_view(), name="respondent-address"),
    path("your-email", views.Email.as_view(), name="email"),
    path("phone-numbers", views.ContactPhone.as_view(), name="contact-phone"),
    path("occupant-name", views.OccupantName.as_view(), name="occupant-name"),
    path(
        "property-postcode", views.PropertyPostcode.as_view(), name="property-postcode"
    ),
    path("property-address", views.PropertyAddress.as_view(), name="property-address"),
    path("address-unknown", views.AddressUnknown.as_view(), name="address-unknown"),
    path("thank-you", views.ThankYou.as_view(), name="thank-you"),
    path("property-tenure", views.Tenure.as_view(), name="tenure"),
    path("consents", views.Consents.as_view(), name="consents"),
    path(
        "property-summary",
        views.PropertyMeasuresSummary.as_view(),
        name="property-measures-summary",
    ),
    path("occupants", views.Occupants.as_view(), name="occupants"),
    path("income", views.HouseholdIncome.as_view(), name="household-income"),
    path(
        "take-home-pay",
        views.HouseholdTakeHomeIncome.as_view(),
        name="household-take-home-income",
    ),
    path(
        "disability-benefits",
        views.DisabilityBenefits.as_view(),
        name="disability-benefits",
    ),
    path("child-benefit", views.ChildBenefit.as_view(), name="child-benefit"),
    path(
        "child-benefit-number",
        views.ChildBenefitNumber.as_view(),
        name="child-benefit-number",
    ),
    path(
        "child-benefit-claimant-type",
        views.ChildBenefitClaimantType.as_view(),
        name="child-benefit-claimant-type",
    ),
    path(
        "child-benefit-summary",
        views.ChildBenefitSummary.as_view(),
        name="child-benefit-summary",
    ),
    path(
        "qualifying-income",
        views.IncomeLtChildBenefitThreshold.as_view(),
        name="income-lt-child-benefit-threshold",
    ),
    path("vulnerabilities", views.Vulnerabilities.as_view(), name="vulnerabilities"),
    path("answers-summary", views.AnswersSummary.as_view(), name="answers-summary"),
    path(
        "recommended-measures",
        views.RecommendedMeasures.as_view(),
        name="recommended-measures",
    ),
]
