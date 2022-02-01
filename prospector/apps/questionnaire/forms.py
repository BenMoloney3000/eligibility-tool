import logging

from django import forms
from django.utils.safestring import mark_safe

from . import enums
from . import models
from prospector.dataformats import phone_numbers
from prospector.dataformats import postcodes


logger = logging.getLogger(__name__)


BOOLEAN_FIELD_CHOICES = [("True", True), ("False", False)]


class BooleanChoiceField(forms.ChoiceField):
    _choices = BOOLEAN_FIELD_CHOICES


class StyledErrorList(forms.utils.ErrorList):

    # (Since Django seems to prefer putting markup in the logic to writing more
    # flexible template tags)

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ""
        return mark_safe('<div class="input-error">%s</div>' % "<br>".join(self))


class AnswerFormMixin:
    """Set the error class and receive questionnaire data."""

    def __init__(self, *args, **kwargs):
        self.signup = kwargs.pop("answers")
        super().__init__(*args, **kwargs)

        # Most fields are required in the form but not the model, reflect this.
        if hasattr(self, "Meta"):
            for field in self.fields:
                if field not in getattr(self.Meta, "optional_fields", []):
                    self.fields[field].required = True

        self.error_class = StyledErrorList


class DummyForm(AnswerFormMixin, forms.Form):
    """Use on pages on which there aren't any questions."""

    pass


class RespondentName(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        fields = [
            "first_name",
            "last_name",
        ]


class RespondentRelationship(AnswerFormMixin, forms.ModelForm):
    respondent_has_permission = forms.ChoiceField(
        choices=BOOLEAN_FIELD_CHOICES, required=True
    )

    class Meta:
        model = models.Answers
        optional_fields = ["respondent_relationship_other"]
        fields = [
            "respondent_relationship",
            "respondent_relationship_other",
            "respondent_has_permission",
        ]

    def clean(self):
        data = super().clean()
        if (
            data.get("respondent_relationship") == enums.RespondentRelationship.OTHER
            and data.get("respondent_relationship_other", "") == ""
        ):
            self.add_error(
                "respondent_relationship_other",
                "Please describe your relationship to the occupant",
            )

        return data


class RespondentAddress(AnswerFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Get the prefilled addresses to populate the select field
        prefilled_addresses = kwargs.pop("prefilled_addresses")
        super().__init__(*args, **kwargs)

        self.prefilled_addresses = prefilled_addresses

        uprn_choices = [
            (uprn, house.address_1) for uprn, house in prefilled_addresses.items()
        ]
        uprn_choices.insert(0, (None, "Address not in list"))

        self.fields["uprn"] = forms.ChoiceField(required=False, choices=uprn_choices)

    class Meta:
        model = models.Answers
        optional_fields = ["address_1", "address_2", "address_3", "uprn"]
        fields = [
            "address_1",
            "address_2",
            "address_3",
            "uprn",
        ]

    def clean_uprn(self):
        uprn = self.cleaned_data["uprn"]
        if uprn not in self.prefilled_addresses:
            self.add_error("uprn", "Invalid value selected")
        else:
            if self.prefilled_addresses[uprn].district != "Plymouth":
                self.add_error(
                    "uprn", "This property is not within the Plymouth Council area."
                )
        return uprn

    def clean(self):
        """Check we got enough data, since no field is actually required."""
        data = super().clean()

        if not data.get("uprn") and not data.get("address_1"):
            self.add_error(
                "address_1",
                "Please enter the first line of an address or select an address from the list",
            )

        return data


class RespondentPhone(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        fields = [
            "contact_phone",
            "contact_preference",
        ]

    def clean_contact_phone(self):
        phone = self.cleaned_data["contact_phone"]
        try:
            phone = phone_numbers.normalise(phone)

        except phone_numbers.ParseError as e:
            self.add_error("contact_phone", e)

        return phone


class OccupantName(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        fields = [
            "occupant_first_name",
            "occupant_last_name",
        ]


class PropertyAddress(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        optional_fields = ["property_address_2", "property_address_3"]
        fields = [
            "property_address_1",
            "property_address_2",
            "property_address_3",
            "property_postcode",
        ]

    def clean_property_postcode(self):
        postcode = self.cleaned_data["property_postcode"]
        postcode = postcodes.normalise(postcode)

        if not postcodes.validate_household_postcode(postcode):
            self.add_error(
                "property_postcode",
                "This does not appear to be a valid UK domestic postcode. Please check and re-enter",
            )

        return postcode


class Consents(AnswerFormMixin, forms.Form):
    call_back = forms.BooleanField(
        required=False, label="To call/email you back to provide advice"
    )
    assess_eligibility = forms.BooleanField(
        required=False,
        label="To use the details you have provided to assess eligibility for current schemes",
    )
    retain_details = forms.BooleanField(
        required=False,
        label=(
            "To hold your details on file and contact you when we think there are schemes "
            "that are relevant for you"
        ),
    )
    anonymous_reporting = forms.BooleanField(
        required=False,
        label=(
            "To use in anonymised reporting that relates to the energy efficiency "
            "of properties in the Plymouth City Council administrative area"
        ),
    )

    def clean_assess_eligibility(self):
        assess_eligibility_consent = self.cleaned_data["assess_eligibility"]
        if not assess_eligibility_consent:
            self.add_error(
                "assess_eligibility",
                "If you do not give us consent to assess your eligibility we cannot help you.",
            )

        return assess_eligibility_consent
