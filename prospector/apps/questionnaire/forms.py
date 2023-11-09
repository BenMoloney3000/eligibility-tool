import logging

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Field
from crispy_forms_gds.layout import Layout
from django import forms
from django.utils.safestring import mark_safe

from . import enums
from . import models
from prospector.dataformats import phone_numbers

logger = logging.getLogger(__name__)


BOOLEAN_FIELD_CHOICES = [("True", True), ("False", False)]
CORRECTION_FIELD_CHOICES = [
    (False, "This seems right"),
    (True, "I would like to correct this"),
]


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
        return mark_safe('<span class="input-error">%s</span>' % "<br>".join(self))


class AnswerFormMixin:
    """Set the error class and receive questionnaire data."""

    def __init__(self, *args, **kwargs):
        self.answers = kwargs.pop("answers")
        super().__init__(*args, **kwargs)

        # Most fields are required in the form but not the model, reflect this.
        if hasattr(self, "Meta"):
            for field in self.fields:
                if field not in getattr(self.Meta, "optional_fields", []):
                    self.fields[field].required = True

        self.error_class = StyledErrorList


class PrePoppedMixin:
    """Pre-populate fields with guesses from property data.

    Look through the form fields to see if any have _orig data. If so use this as
    the initial value, and add in an 'agree' field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only one agree field per page.
        add_agree_field = False

        if hasattr(self, "Meta"):
            for field in self.fields:
                epc_datafield = field + "_orig"
                if hasattr(self.answers, epc_datafield):
                    # Check there's a value else we keep quiet
                    value = getattr(self.answers, epc_datafield)
                    if value:
                        # We have one.
                        add_agree_field = True
                        if not self.initial[field]:
                            self.initial[field] = value

            if add_agree_field:
                self.fields["data_correct"] = forms.TypedChoiceField(
                    coerce=lambda x: x == "True",
                    choices=((True, "Yes"), (False, "No")),
                    widget=forms.RadioSelect,
                    required=True,
                )
                self.fields["data_correct"].label = "Is this correct?"


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


class RespondentRole(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        optional_fields = ["respondent_role_other"]
        fields = [
            "respondent_role",
            "respondent_role_other",
        ]

    def clean(self):
        data = super().clean()
        if (
            data.get("respondent_role") == enums.RespondentRole.OTHER
            and data.get("respondent_role_other", "") == ""
        ):
            self.add_error(
                "respondent_role_other",
                "Please describe your relationship to the owner or occupant",
            )

        return data


class RespondentAddress(AnswerFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Get the prefilled addresses to populate the select field
        prefilled_addresses = kwargs.pop("prefilled_addresses")
        super().__init__(*args, **kwargs)

        self.prefilled_addresses = prefilled_addresses

        udprn_choices = [
            (udprn, f"{house.line_1}, {house.line_2}".strip(", "))
            for udprn, house in prefilled_addresses.items()
        ]
        udprn_choices.append((None, "Address not in the list"))
        udprn_choices.insert(0, (None, "Click here to choose the address"))
        self.fields["respondent_udprn"] = forms.ChoiceField(
            required=False, choices=udprn_choices
        )

        self.initial["respondent_udprn"] = udprn_choices[0][0]

    class Meta:
        model = models.Answers
        optional_fields = [
            "respondent_address_1",
            "respondent_address_2",
            "respondent_address_3",
            "respondent_udprn",
        ]
        fields = [
            "respondent_address_1",
            "respondent_address_2",
            "respondent_address_3",
            "respondent_udprn",
        ]

    def clean(self):
        """Check we got enough data, since no field is actually required."""
        data = super().clean()

        if not data.get("respondent_udprn") and not data.get("respondent_address_1"):
            self.add_error(
                "respondent_address_1",
                "Please enter the first line of an address or select an address from the list",
            )

        return data


class RespondentPhone(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        fields = ["contact_phone", "contact_mobile"]
        optional_fields = ["contact_phone", "contact_mobile"]

    def clean_contact_phone(self):
        phone = self.cleaned_data["contact_phone"]
        if phone:
            try:
                phone = phone_numbers.normalise(phone)

            except phone_numbers.ParseError as e:
                self.add_error("contact_phone", e)

        return phone

    def clean_contact_mobile(self):
        phone = self.cleaned_data["contact_mobile"]
        if phone:
            try:
                phone = phone_numbers.normalise(phone)

            except phone_numbers.ParseError as e:
                self.add_error("contact_mobile", e)

        return phone

    def clean(self):
        # Ensure we've got at least one phone number
        if (
            not self.cleaned_data["contact_mobile"]
            and not self.cleaned_data["contact_phone"]
        ):
            self.add_error(
                "contact_phone", "Please enter at least one telephone number"
            )


class OccupantName(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        fields = [
            "occupant_first_name",
            "occupant_last_name",
        ]


class AnswersSummary(AnswerFormMixin, forms.ModelForm):
    source_of_info_about_pec = forms.ChoiceField(
        required=True,
        choices=enums.HowDidYouHearAboutPEC.choices,
    )

    def clean_source_of_info_about_pec(self):
        data = self.cleaned_data.get("source_of_info_about_pec")
        if data == enums.HowDidYouHearAboutPEC.LABEL:
            raise forms.ValidationError("This field is required")
        return data

    class Meta:
        model = models.Answers
        fields = [
            "source_of_info_about_pec",
        ]


class PropertyAddress(AnswerFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Get the prefilled addresses to populate the select field
        prefilled_addresses = kwargs.pop("prefilled_addresses")
        super().__init__(*args, **kwargs)

        self.prefilled_addresses = prefilled_addresses

        address_choices = [
            (id, f"{house.address_1}, {house.address_2}".strip(", "))
            for id, house in prefilled_addresses.items()
        ]
        address_choices.append((None, "Address not in the list"))
        address_choices.insert(0, (None, "Click here to choose the address"))

        self.fields["chosen_address"] = forms.ChoiceField(
            required=False,
            choices=address_choices,
        )
        self.initial["chosen_address"] = address_choices[0][0]

    class Meta:
        model = models.Answers
        optional_fields = [
            "property_address_1",
            "property_address_2",
            "property_address_3",
        ]
        fields = [
            "property_address_1",
            "property_address_2",
            "property_address_3",
        ]

    def clean(self):
        """Check we got enough data, since no field is actually required."""
        data = super().clean()

        if not data.get("property_udprn") and not data.get("property_address_1"):
            self.add_error(
                "property_address_1",
                "Please enter the first line of an address or select an address from the drop-down list above",
            )

        return data


class Consents(AnswerFormMixin, forms.ModelForm):
    consented_callback = forms.BooleanField(
        required=False, label="To call or email you to offer advice and help."
    )
    consented_future_schemes = forms.BooleanField(
        required=False,
        label=(
            "To contact you in the future when we think there are grants or "
            "programmes relevant for you."
        ),
    )

    class Meta:
        model = models.Answers
        optional_fields = ["consented_callback", "consented_future_schemes"]
        fields = ["consented_callback", "consented_future_schemes"]

    def clean(self):
        """If fields weren't submitted, make them False."""

        data = super().clean()
        if data.get("consented_callback") is None:
            data["consented_callback"] = False
        if data.get("consented_future_schemes") is None:
            data["consented_future_schemes"] = False

        return data


class PropertyMeasuresSummary(AnswerFormMixin, forms.ModelForm):
    respondent_comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
    )

    class Meta:
        model = models.Answers
        optional_fields = ["respondent_comments"]
        fields = ["respondent_comments"]


class PropertyType(AnswerFormMixin, PrePoppedMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Answers
        fields = [
            "property_type",
            "property_attachment",
        ]


class Occupants(AnswerFormMixin, forms.ModelForm):
    adults = forms.ChoiceField(required=True, choices=enums.OneToFourOrMore.choices)
    children = forms.ChoiceField(required=True, choices=enums.UpToFourOrMore.choices)
    seniors = forms.ChoiceField(required=True, choices=enums.UpToFourOrMore.choices)

    class Meta:
        model = models.Answers
        fields = [
            "adults",
            "children",
            "seniors",
        ]


class Vulnerabilities(AnswerFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout()
        for (
            name,
            field,
        ) in self.fields.items():
            self.helper.layout.append(Field(name))

    class Meta:
        model = models.Answers
        fields = [
            "vulnerable_cariovascular",
            "vulnerable_respiratory",
            "vulnerable_mental_health",
            "vulnerable_cns",
            "vulnerable_disability",
            "vulnerable_age",
            "vulnerable_child_pregnancy",
        ]
        optional_fields = fields
        widgets = {
            "vulnerable_cariovascular": forms.CheckboxInput(),
            "vulnerable_respiratory": forms.CheckboxInput(),
            "vulnerable_mental_health": forms.CheckboxInput(),
            "vulnerable_cns": forms.CheckboxInput(),
            "vulnerable_disability": forms.CheckboxInput(),
            "vulnerable_age": forms.CheckboxInput(),
            "vulnerable_child_pregnancy": forms.CheckboxInput(),
        }
        labels = {
            "vulnerable_cariovascular": (
                "A cardiovascular condition (for example: heart condition, risk "
                "of stroke, high blood pressure etc.)"
            ),
            "vulnerable_respiratory": (
                "A respiratory condition (for example COPD or asthma)"
            ),
            "vulnerable_mental_health": ("A mental health condition"),
            "vulnerable_cns": (
                "A central nervous system condition (for example dementia, "
                "Alzheimer's or fibromyalgia)"
            ),
            "vulnerable_disability": ("Disability"),
            "vulnerable_age": ("Being over 65 years old"),
            "vulnerable_child_pregnancy": (
                "Being a child under the age of five, or being pregnant"
            ),
        }


class ChildBenefitSummary(AnswerFormMixin, forms.ModelForm):
    confirm_or_amend = forms.ChoiceField(
        choices=[
            ("YES", "Yes"),
            ("AMEND", "No - I need to amend the information I have given"),
        ],
        widget=forms.RadioSelect,
        required=True,
        label=("I confirm this is an accurate description of my household members"),
    )

    class Meta:
        model = models.Answers
        fields = ["confirm_or_amend"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout()
