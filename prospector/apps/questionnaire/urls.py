from django.urls import path

from .views import trail as views

app_name = "questionnaire"

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("start", views.Start.as_view(), name="start"),
    path("name", views.RespondentName.as_view(), name="respondent-name"),
    path("role", views.RespondentRole.as_view(), name="respondent-role"),
    path(
        "permission",
        views.RespondentHasPermission.as_view(),
        name="respondent-has-permission",
    ),
    path("need-permission", views.NeedPermission.as_view(), name="need-permission"),
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
    path(
        "disruption", views.ToleratedDisruption.as_view(), name="tolerated-disruption"
    ),
    path("state-of-repair", views.StateOfRepair.as_view(), name="state-of-repair"),
    path("motivations", views.Motivations.as_view(), name="motivations"),
    path(
        "owner-contributions",
        views.ContributionCapacity.as_view(),
        name="contribution-capacity",
    ),
    path("no-funding", views.NothingAtThisTime.as_view(), name="nothing-at-this-time"),
    path("adult-1-name", views.Adult1Name.as_view(), name="adult1-name"),
    path(
        "adult-1-employment", views.Adult1Employment.as_view(), name="adult1-employment"
    ),
    path(
        "adult-1-employment-income",
        views.Adult1EmploymentIncome.as_view(),
        name="adult1-employment-income",
    ),
    path(
        "adult-1-self-employment-income",
        views.Adult1SelfEmploymentIncome.as_view(),
        name="adult1-self-employment-income",
    ),
    path(
        "adult-1-welfare-benefits",
        views.Adult1WelfareBenefits.as_view(),
        name="adult1-welfare-benefits",
    ),
    path(
        "adult-1-welfare-benefit-amounts",
        views.Adult1WelfareBenefitAmounts.as_view(),
        name="adult1-welfare-benefit-amounts",
    ),
    path(
        "adult-1-pension-income",
        views.Adult1PensionIncome.as_view(),
        name="adult1-pension-income",
    ),
    path(
        "adult-1-savings-income",
        views.Adult1SavingsIncome.as_view(),
        name="adult1-savings-income",
    ),
    path("adult-2-name", views.Adult2Name.as_view(), name="adult2-name"),
    path(
        "adult-2-employment", views.Adult2Employment.as_view(), name="adult2-employment"
    ),
    path(
        "adult-2-employment-income",
        views.Adult2EmploymentIncome.as_view(),
        name="adult2-employment-income",
    ),
    path(
        "adult-2-self-employment-income",
        views.Adult2SelfEmploymentIncome.as_view(),
        name="adult2-self-employment-income",
    ),
    path(
        "adult-2-welfare-benefits",
        views.Adult2WelfareBenefits.as_view(),
        name="adult2-welfare-benefits",
    ),
    path(
        "adult-2-welfare-benefit-amounts",
        views.Adult2WelfareBenefitAmounts.as_view(),
        name="adult2-welfare-benefit-amounts",
    ),
    path(
        "adult-2-pension-income",
        views.Adult2PensionIncome.as_view(),
        name="adult2-pension-income",
    ),
    path(
        "adult-2-savings-income",
        views.Adult2SavingsIncome.as_view(),
        name="adult2-savings-income",
    ),
    path("adult-3-name", views.Adult3Name.as_view(), name="adult3-name"),
    path(
        "adult-3-employment", views.Adult3Employment.as_view(), name="adult3-employment"
    ),
    path(
        "adult-3-employment-income",
        views.Adult3EmploymentIncome.as_view(),
        name="adult3-employment-income",
    ),
    path(
        "adult-3-self-employment-income",
        views.Adult3SelfEmploymentIncome.as_view(),
        name="adult3-self-employment-income",
    ),
    path(
        "adult-3-welfare-benefits",
        views.Adult3WelfareBenefits.as_view(),
        name="adult3-welfare-benefits",
    ),
    path(
        "adult-3-welfare-benefit-amounts",
        views.Adult3WelfareBenefitAmounts.as_view(),
        name="adult3-welfare-benefit-amounts",
    ),
    path(
        "adult-3-pension-income",
        views.Adult3PensionIncome.as_view(),
        name="adult3-pension-income",
    ),
    path(
        "adult-3-savings-income",
        views.Adult3SavingsIncome.as_view(),
        name="adult3-savings-income",
    ),
    path("adult-4-name", views.Adult4Name.as_view(), name="adult4-name"),
    path(
        "adult-4-employment", views.Adult4Employment.as_view(), name="adult4-employment"
    ),
    path(
        "adult-4-employment-income",
        views.Adult4EmploymentIncome.as_view(),
        name="adult4-employment-income",
    ),
    path(
        "adult-4-self-employment-income",
        views.Adult4SelfEmploymentIncome.as_view(),
        name="adult4-self-employment-income",
    ),
    path(
        "adult-4-welfare-benefits",
        views.Adult4WelfareBenefits.as_view(),
        name="adult4-welfare-benefits",
    ),
    path(
        "adult-4-welfare-benefit-amounts",
        views.Adult4WelfareBenefitAmounts.as_view(),
        name="adult4-welfare-benefit-amounts",
    ),
    path(
        "adult-4-pension-income",
        views.Adult4PensionIncome.as_view(),
        name="adult4-pension-income",
    ),
    path(
        "adult-4-savings-income",
        views.Adult4SavingsIncome.as_view(),
        name="adult4-savings-income",
    ),
    path("summary", views.HouseholdSummary.as_view(), name="household-summary"),
    path("answers-summary", views.AnswersSummary.as_view(), name="answers-summary"),
    path("eligibility", views.EligibilitySummary.as_view(), name="eligibility-summary"),
    path(
        "recommended-measures",
        views.RecommendedMeasures.as_view(),
        name="recommended-measures",
    ),
    path("complete", views.Completed.as_view(), name="completed"),
]
