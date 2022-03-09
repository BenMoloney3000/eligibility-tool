from django.urls import path

from .views import trail as views

app_name = "questionnaire"

urlpatterns = [
    path("", views.Start.as_view(), name="start"),
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
    path(
        "property-ownership",
        views.PropertyOwnership.as_view(),
        name="property-ownership",
    ),
    path("consents", views.Consents.as_view(), name="consents"),
    path("epc", views.SelectEPC.as_view(), name="select-e-p-c"),
    path("data", views.InferredData.as_view(), name="inferred-data"),
    path("type", views.PropertyType.as_view(), name="property-type"),
    path("age", views.PropertyAgeBand.as_view(), name="property-age-band"),
    path("wall-type", views.WallType.as_view(), name="wall-type"),
    path("wall-insulation", views.WallsInsulated.as_view(), name="walls-insulated"),
    path("floor-type", views.SuspendedFloor.as_view(), name="suspended-floor"),
    path(
        "floor-insulation",
        views.SuspendedFloorInsulated.as_view(),
        name="suspended-floor-insulated",
    ),
    path("unheated-loft", views.UnheatedLoft.as_view(), name="unheated-loft"),
    path("loft-conversion", views.RoomInRoof.as_view(), name="room-in-roof"),
    path(
        "loft-conversion-insulated", views.RirInsulated.as_view(), name="rir-insulated"
    ),
    path(
        "loft-insulation",
        views.RoofSpaceInsulated.as_view(),
        name="roof-space-insulated",
    ),
    path("flat-roof", views.FlatRoof.as_view(), name="flat-roof"),
    path(
        "flat-roof-insulated",
        views.FlatRoofInsulated.as_view(),
        name="flat-roof-insulated",
    ),
    path("gas-boiler", views.GasBoilerPresent.as_view(), name="gas-boiler-present"),
    path("hot-water-tank", views.HwtPresent.as_view(), name="hwt-present"),
    path("mains-gas", views.OnMainsGas.as_view(), name="on-mains-gas"),
    path(
        "other-heating-system",
        views.OtherHeatingPresent.as_view(),
        name="other-heating-present",
    ),
    path("heat-pump", views.HeatPumpPresent.as_view(), name="heat-pump-present"),
    path("heating-fuel", views.OtherHeatingFuel.as_view(), name="other-heating-fuel"),
    path("boiler-age", views.GasBoilerAge.as_view(), name="gas-boiler-age"),
    path("boiler-condition", views.GasBoilerBroken.as_view(), name="gas-boiler-broken"),
    path("heating-controls", views.HeatingControls.as_view(), name="heating-controls"),
    path(
        "storage-heaters",
        views.StorageHeatersPresent.as_view(),
        name="storage-heaters-present",
    ),
    path(
        "electric-radiators",
        views.ElectricRadiatorsPresent.as_view(),
        name="electric-radiators-present",
    ),
    path(
        "storage-heater-performance",
        views.HhrshsPresent.as_view(),
        name="hhrshs-present",
    ),
    path(
        "conservation-area",
        views.InConservationArea.as_view(),
        name="in-conservation-area",
    ),
    path("accuracy-warning", views.AccuracyWarning.as_view(), name="accuracy-warning"),
    path(
        "recommendations",
        views.RecommendedMeasures.as_view(),
        name="recommended-measures",
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
    path("eligibility", views.EligibilitySummary.as_view(), name="eligibility-summary"),
    path("complete", views.Completed.as_view(), name="completed"),
]
