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
    path(
        "disruption", views.ToleratedDisruption.as_view(), name="tolerated-disruption"
    ),
    path("motivations", views.Motivations.as_view(), name="motivations"),
    path(
        "eligibility", views.PropertyEligibility.as_view(), name="property-eligibility"
    ),
]
