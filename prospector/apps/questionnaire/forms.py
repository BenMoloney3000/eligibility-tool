import logging

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Div
from crispy_forms_gds.layout import Field
from crispy_forms_gds.layout import Fieldset
from crispy_forms_gds.layout import Layout
from django import forms
from django.utils.safestring import mark_safe

from . import enums
from . import models
from . import utils
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
        udprn_choices.append((None, "Address not in list"))
        self.fields["respondent_udprn"] = forms.ChoiceField(
            required=False, choices=udprn_choices
        )

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


class PropertyAddress(AnswerFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Get the prefilled addresses to populate the select field
        prefilled_addresses = kwargs.pop("prefilled_addresses")
        super().__init__(*args, **kwargs)

        self.prefilled_addresses = prefilled_addresses

        udprn_choices = [
            (udprn, f"{house.line_1}, {house.line_2}".strip(", "))
            for udprn, house in prefilled_addresses.items()
        ]
        udprn_choices.append((None, "Address not in list"))

        self.fields["property_udprn"] = forms.ChoiceField(
            required=False, choices=udprn_choices
        )

    class Meta:
        model = models.Answers
        optional_fields = [
            "property_address_1",
            "property_address_2",
            "property_address_3",
            "property_udprn",
        ]
        fields = [
            "property_address_1",
            "property_address_2",
            "property_address_3",
            "property_udprn",
        ]

    def clean_udprn(self):
        udprn = self.cleaned_data["property_udprn"]
        if udprn not in self.prefilled_addresses:
            self.add_error("property_udprn", "Invalid value selected")
        else:
            # Ideal Postcodes and Data8 report the administrative district differently
            # and we want it to work with either, including old cached values
            if self.prefilled_addresses[udprn].district not in [
                "City of Plymouth",
                "Plymouth",
            ]:
                self.add_error(
                    "property_udprn",
                    "This property is not within the Plymouth Council area.",
                )
        return udprn

    def clean(self):
        """Check we got enough data, since no field is actually required."""
        data = super().clean()

        if not data.get("property_udprn") and not data.get("property_address_1"):
            self.add_error(
                "property_address_1",
                "Please enter the first line of an address or select an address from the list",
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


class SelectEPC(AnswerFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Get the candidate EPCs to populate the select field
        candidate_epcs = kwargs.pop("candidate_epcs")
        super().__init__(*args, **kwargs)

        self.candidate_epcs = candidate_epcs

        epc_choices = [(lmk_id, str(epc)) for lmk_id, epc in candidate_epcs.items()]
        epc_choices.append((None, "No valid EPC"))
        self.fields["selected_epc"] = forms.ChoiceField(
            required=False, choices=epc_choices, initial=epc_choices[0][0]
        )

    class Meta:
        model = models.Answers
        fields = [
            "selected_epc",
        ]


class PropertyType(AnswerFormMixin, PrePoppedMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Answers
        fields = [
            "property_type",
            "property_form",
        ]


class HeatingControls(AnswerFormMixin, forms.ModelForm):
    trvs_present = forms.ChoiceField(
        choices=enums.TRVsPresent.choices,
        widget=forms.RadioSelect,
        required=True,
        label=(
            "Adjustable TRV controls on your radiators (Thermostatically "
            "Radiator Valves - turn valves that are positioned at one end of a "
            "radiator)"
        ),
    )
    room_thermostat = forms.TypedChoiceField(
        coerce=lambda x: x == "True",
        choices=((True, "Yes"), (False, "No")),
        widget=forms.RadioSelect,
        required=True,
        label=(
            "One or more room thermostats (set the desired temperature in "
            "the room they are positioned in)."
        ),
    )
    ch_timer = forms.TypedChoiceField(
        coerce=lambda x: x == "True",
        choices=((True, "Yes"), (False, "No")),
        widget=forms.RadioSelect,
        required=True,
        label=(
            "A central heating timer (a timer or programmer allows you to "
            "control when your heating and hot water comes on and when it goes "
            "off)."
        ),
    )
    programmable_thermostat = forms.TypedChoiceField(
        coerce=lambda x: x == "True",
        choices=((True, "Yes"), (False, "No")),
        widget=forms.RadioSelect,
        required=True,
        label=(
            "A programmable central heating thermostat (combines time and "
            "temperature controls in a single unit)."
        ),
    )
    smart_thermostat = forms.TypedChoiceField(
        coerce=lambda x: x == "True",
        choices=((True, "Yes"), (False, "No")),
        widget=forms.RadioSelect,
        required=True,
        label=(
            "A smart thermostat system (more advanced control systems for "
            "central heating that set temperature and timing and are connected "
            "to the internet)."
        ),
    )

    class Meta:
        model = models.Answers
        fields = [
            "trvs_present",
            "room_thermostat",
            "ch_timer",
            "programmable_thermostat",
            "smart_thermostat",
        ]


class Occupants(AnswerFormMixin, forms.ModelForm):
    adults = forms.ChoiceField(required=True, choices=enums.OneToFourOrMore.choices)
    children = forms.ChoiceField(required=True, choices=enums.UpToFourOrMore.choices)

    class Meta:
        model = models.Answers
        fields = [
            "adults",
            "children",
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
                "of stroke, high blood pressure etc."
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


class Motivations(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        fields = [
            "motivation_better_comfort",
            "motivation_lower_bills",
            "motivation_unknown",
            "motivation_environment",
        ]
        optional_fields = fields
        widgets = {
            "motivation_better_comfort": forms.CheckboxInput(),
            "motivation_lower_bills": forms.CheckboxInput(),
            "motivation_unknown": forms.CheckboxInput(),
            "motivation_environment": forms.CheckboxInput(),
        }
        labels = {
            "motivation_better_comfort": "A more comfortable property",
            "motivation_lower_bills": "Reducing energy and heating bills",
            "motivation_unknown": "I don't know",
            "motivation_environment": "A greener property - doing your bit to tackle climate change",
        }


"""
# Forms for each adult in the household, for respondents that need to answer this.
"""


class HouseholdAdultName(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.HouseholdAdult
        fields = ["first_name", "last_name"]


class HouseholdAdultEmployment(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.HouseholdAdult
        fields = ["employment_status"]


class HouseholdAdultEmploymentIncome(AnswerFormMixin, forms.ModelForm):
    employed_income_frequency = forms.ChoiceField(
        choices=enums.PaymentFrequency.choices, required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout()
        self.helper.layout.append(
            Fieldset(
                Div(
                    Field(
                        f"employed_income",
                        spellcheck="false",
                        template="questionnaire/fields/money_field.html",
                    ),
                    Field(f"employed_income_frequency"),
                    css_class="fieldset_row",
                ),
                legend="",
            )
        )

    class Meta:
        model = models.HouseholdAdult
        fields = ["employed_income", "employed_income_frequency"]


class HouseholdAdultSelfEmploymentIncome(AnswerFormMixin, forms.ModelForm):
    self_employed_income_frequency = forms.ChoiceField(
        choices=enums.PaymentFrequency.choices, required=True
    )
    business_income_frequency = forms.ChoiceField(
        choices=enums.PaymentFrequency.choices, required=True
    )

    class Meta:
        model = models.HouseholdAdult
        optional_fields = ["business_income", "business_income_frequency"]
        fields = [
            "self_employed_income",
            "self_employed_income_frequency",
            "business_income",
            "business_income_frequency",
        ]


class HouseholdAdultWelfareBenefits(AnswerFormMixin, forms.Form):

    field_labels = {
        "uc": "Universal Credit",
        "jsa": "Job Seekers Allowance (JSA)",
        "esa": "Employment and Support Allowance (ESA)",
        "income_support": "Income Support",
        "child_tax_credit": "Child Tax Credit",
        "working_tax_credit": "Working Tax Credit",
        "child_benefit": "Child Benefit",
        "housing_benefit": "Housing Benefit",
        "attendance_allowance": "Attendance Allowance",
        "carers_allowance": "Carers Allowance",
        "dla": "Disability Living Allowance (DLA)",
        "pip": "Personal Independence Payment (PIP)",
        "pension_credit": "Pension Credit",
        "other": "Other",
    }

    uc = forms.BooleanField(required=False)
    jsa = forms.BooleanField(required=False)
    esa = forms.BooleanField(required=False)
    income_support = forms.BooleanField(required=False)
    child_tax_credit = forms.BooleanField(required=False)
    working_tax_credit = forms.BooleanField(required=False)
    child_benefit = forms.BooleanField(required=False)
    housing_benefit = forms.BooleanField(required=False)
    attendance_allowance = forms.BooleanField(required=False)
    carers_allowance = forms.BooleanField(required=False)
    dla = forms.BooleanField(required=False)
    pip = forms.BooleanField(required=False)
    pension_credit = forms.BooleanField(required=False)
    other = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.household_adult = kwargs.pop("household_adult")
        super().__init__(*args, **kwargs)

        # Set initial values from related models the fields dynamically
        self.benefits = models.WelfareBenefit.objects.filter(
            recipient=self.household_adult
        )

        for benefit in self.benefits:
            self.initial[benefit.benefit_type.lower()] = True

        for name, field in self.fields.items():
            field.label = self.field_labels[name]


class HouseholdAdultWelfareBenefitAmounts(AnswerFormMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        self.household_adult = kwargs.pop("household_adult")
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout()

        # Instantiate the fields dynamically
        self.benefits = models.WelfareBenefit.objects.filter(
            recipient=self.household_adult
        )

        for benefit in self.benefits:
            field_prefix = benefit.benefit_type.lower()
            self.fields[f"{field_prefix}_amount"] = forms.IntegerField(
                required=True,
                min_value=1,
                max_value=32767,
                label="",
            )
            self.initial[f"{field_prefix}_amount"] = benefit.amount
            self.fields[f"{field_prefix}_frequency"] = forms.ChoiceField(
                required=True, choices=enums.BenefitPaymentFrequency.choices, label=""
            )
            self.initial[f"{field_prefix}_frequency"] = benefit.frequency

            self.helper.layout.append(
                Fieldset(
                    Div(
                        Field(
                            f"{field_prefix}_amount",
                            spellcheck="false",
                            template="questionnaire/fields/money_field.html",
                        ),
                        Field(f"{field_prefix}_frequency"),
                        css_class="fieldset_row",
                    ),
                    legend=enums.BenefitType(benefit.benefit_type).label,
                )
            )


class HouseholdAdultPensionIncome(AnswerFormMixin, forms.ModelForm):
    private_pension_income_frequency = forms.ChoiceField(
        choices=enums.PaymentFrequency.choices, required=True, label="Frequency"
    )
    state_pension_income_frequency = forms.ChoiceField(
        choices=enums.PaymentFrequency.choices, required=True, label="Frequency"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout()
        self.helper.layout.append(
            Fieldset(
                Div(
                    Field(
                        f"private_pension_income",
                        spellcheck="false",
                        template="questionnaire/fields/money_field.html",
                    ),
                    Field(
                        f"private_pension_income_frequency",
                    ),
                    css_class="fieldset_row",
                ),
                legend="Private Pension(s)",
            ),
        )
        self.helper.layout.append(
            Fieldset(
                Div(
                    Field(
                        f"state_pension_income",
                        spellcheck="false",
                        template="questionnaire/fields/money_field.html",
                    ),
                    Field(f"state_pension_income_frequency"),
                    css_class="fieldset_row",
                ),
                legend="State Pension",
            )
        )

    class Meta:
        model = models.HouseholdAdult
        fields = [
            "private_pension_income",
            "private_pension_income_frequency",
            "state_pension_income",
            "state_pension_income_frequency",
        ]
        labels = {
            "private_pension_income": "Income",
            "state_pension_income": "Income",
        }


class HouseholdAdultSavingsIncome(AnswerFormMixin, forms.ModelForm):
    saving_investment_income_frequency = forms.ChoiceField(
        choices=enums.PaymentFrequency.choices, required=True, label="Frequency"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout()
        self.helper.layout.append(
            Fieldset(
                Div(
                    Field(
                        f"saving_investment_income",
                        spellcheck="false",
                        template="questionnaire/fields/money_field.html",
                    ),
                    Field(
                        f"saving_investment_income_frequency",
                    ),
                    css_class="fieldset_row",
                ),
                legend="",
            ),
        )

    class Meta:
        model = models.HouseholdAdult
        fields = ["saving_investment_income", "saving_investment_income_frequency"]
        labels = {
            "saving_investment_income": "Income",
        }

    def clean(self):
        data = super().clean()

        income = data.get("saving_investment_income")
        freq = data.get("saving_investment_income_frequency")
        try:
            amt = int(income)

            if amt != 0 and (
                (amt < 200 and freq == enums.PaymentFrequency.ANNUALLY)
                or (amt < 17 and freq == enums.PaymentFrequency.MONTHLY)
            ):
                self.add_error(
                    "saving_investment_income",
                    "If the amount is under £200pa please enter a zero amount.",
                )
        except ValueError:
            self.add_error(
                "saving_investment_income", "Please enter a whole number of pounds."
            )

        return data


class HouseholdSummary(AnswerFormMixin, forms.ModelForm):
    # Allow the user to select 'AMEND', which will not get stored in the DB
    confirm_or_amend_income = forms.ChoiceField(
        choices=[
            ("YES", "Yes"),
            ("AMEND", "No - I need to amend the information I have given"),
            (
                "NO",
                (
                    "No - I didn't have all the information to hand so I have "
                    "only filled this in for some income sources"
                ),
            ),
        ],
        widget=forms.RadioSelect,
        required=True,
    )
    take_home_lt_30k_confirmation = forms.TypedChoiceField(
        coerce=lambda x: x == "True",
        choices=((True, "Yes"), (False, "No")),
        widget=forms.RadioSelect,
        required=False,
    )

    class Meta:
        model = models.Answers
        fields = ["take_home_lt_30k_confirmation"]
        optional_fields = ["take_home_lt_30k_confirmation"]

    def __init__(self, *args, **kwargs):
        """Dynamically whether take_home_lt_30k_confirmation is required.

        (only required if total income > £30k)
        """

        # get self.answers populated:
        super().__init__(*args, **kwargs)
        if utils.calculate_household_income(self.answers) > 30000:
            self.fields["take_home_lt_30k_confirmation"].required = True


class NothingAtThisTime(AnswerFormMixin, forms.ModelForm):
    class Meta:
        model = models.Answers
        fields = ["consented_future_schemes"]
        optional_fields = fields
        widgets = {
            "consented_future_schemes": forms.CheckboxInput(),
        }


class ChildBenefitSummary(AnswerFormMixin, forms.ModelForm):
    confirm_or_amend = forms.ChoiceField(
        choices=[
            ("YES", "Yes"),
            ("AMEND", "No - I need to amend the information I have given"),
        ],
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta:
        model = models.Answers
        fields = ["child_benefit_eligibility_complete"]
