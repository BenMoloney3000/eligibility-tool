import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.views.generic.base import TemplateView

from . import abstract as abstract_views
from prospector.apps.parity.utils import get_addresses_for_postcode
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import forms as questionnaire_forms
from prospector.apps.questionnaire import selectors
from prospector.apps.questionnaire import services
from prospector.apps.questionnaire import utils
from prospector.dataformats import postcodes

logger = logging.getLogger(__name__)


SESSION_ANSWERS_ID = "questionnaire:answer_id"
SESSION_TRAIL_ID = "questionnaire:trail_id"
COMPLETE_TRAIL = 0


class Home(TemplateView):
    template_name = "questionnaire/home.html"


class Start(abstract_views.SingleQuestion):
    template_name = "questionnaire/start.html"
    type_ = abstract_views.QuestionType.YesNo
    title = "About this tool"
    answer_field = "terms_accepted_at"
    question = "Please confirm that you have read and accept our data privacy policy."
    next = "RespondentName"
    percent_complete = COMPLETE_TRAIL

    def pre_save(self):
        self.answers.terms_accepted_at = timezone.now()


class RespondentName(abstract_views.Question):
    title = "Your name"
    template_name = "questionnaire/respondent_name.html"
    next = "RespondentRole"
    percent_complete = COMPLETE_TRAIL + 5
    form_class = questionnaire_forms.RespondentName


class RespondentRole(abstract_views.Question):
    title = "Your role"
    form_class = questionnaire_forms.RespondentRole
    template_name = "questionnaire/respondent_role.html"
    percent_complete = COMPLETE_TRAIL + 10

    def pre_save(self):
        if self.answers.is_occupant:
            # For safety, erase all the details describing a non-occupant respondent
            self.answers.respondent_address_1 = ""
            self.answers.respondent_address_2 = ""
            self.answers.respondent_address_3 = ""
            self.answers.respondent_udprn = ""
            self.answers.respondent_postcode = ""

        if self.answers.respondent_role != enums.RespondentRole.OTHER.value:
            self.answers.respondent_role_other = ""

        if self.answers.respondent_role == enums.RespondentRole.OWNER_OCCUPIER.value:
            self.answers.respondent_has_permission = None

    def get_next(self):
        if self.answers.respondent_role != enums.RespondentRole.OWNER_OCCUPIER.value:
            return "RespondentHasPermission"
        else:
            return "Email"


class RespondentHasPermission(abstract_views.SingleQuestion):
    title = "Householder permission"
    type_ = abstract_views.QuestionType.YesNo
    percent_complete = COMPLETE_TRAIL + 15

    def get_question(self):
        # Wording of question depends on role:
        if self.answers.respondent_role == enums.RespondentRole.TENANT:
            return (
                "Do you have permission from the owner to contact us on their behalf?"
            )
        elif self.answers.respondent_role == enums.RespondentRole.LANDLORD:
            return (
                "Do you have permission from the tenants to contact us on their behalf?"
            )
        else:
            # Other
            return "Do you have permission from the owner and occupants to contact us on their behalf?"

    def get_initial(self):
        data = super().get_initial()

        # Specific case here - initial data from DB can only be true or null, otherwise
        # the whole Answers object gets deleted.
        if data.get("respondent_has_permission"):
            data["respondent_has_permission"] = "True"

        return data

    def get_next(self):
        if not self.answers.respondent_has_permission:
            return "NeedPermission"
        elif self.answers.is_occupant:
            return "Email"
        else:
            return "RespondentPostcode"


class NeedPermission(abstract_views.Question):
    title = "Sorry, we can't help you."
    template_name = "questionnaire/need_permission.html"
    percent_complete = COMPLETE_TRAIL

    def get_initial(self):
        # If we don't have permission, we need to delete everything entered so far
        self.answers.delete()


class RespondentPostcode(abstract_views.SingleQuestion):
    title = "Your postcode"
    type_ = abstract_views.QuestionType.Text
    question = "Enter your postcode"
    supplementary = (
        "This is the postcode for your own address, not that of the property "
        "about which you're enquiring."
    )
    next = "RespondentAddress"
    percent_complete = COMPLETE_TRAIL + 20

    def sanitise_answer(self, data):
        data = postcodes.normalise(data)
        return data

    @staticmethod
    def validate_answer(value):
        if not postcodes.validate_household_postcode(value):
            raise ValidationError(
                "This does not appear to be a valid UK domestic postcode. Please check and re-enter"
            )


class RespondentAddress(abstract_views.Question):
    title = "Your address"
    form_class = questionnaire_forms.RespondentAddress
    template_name = "questionnaire/respondent_address.html"
    next = "Email"
    percent_complete = COMPLETE_TRAIL + 25
    prefilled_addresses = {}

    # Perform the API call to provide the choices for the address
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            self.prefilled_addresses = {
                address.udprn: address
                for address in selectors.get_postcode(self.answers.respondent_postcode)
            }
        except ValueError:
            pass

        kwargs["prefilled_addresses"] = self.prefilled_addresses
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["postcode"] = self.answers.respondent_postcode
        context["all_postcode_addresses"] = {
            key: {
                "address1": address.line_1,
                "address2": address.line_2,
                "address3": address.post_town,
            }
            for key, address in self.prefilled_addresses.items()
        }
        # TODO: fix inconsistency here: property gets three lines of address
        # (because post town of Plymouth is assumed)
        # but respondent can be elsewhere, so effectively gets two lines of
        # address and the third is the post town. Maybe this is fine?
        return context

    def pre_save(self):
        if (
            self.answers.respondent_udprn
            and int(self.answers.respondent_udprn) in self.prefilled_addresses
        ):
            selected_address = self.prefilled_addresses[
                int(self.answers.respondent_udprn)
            ]
            if not self.answers.respondent_address_1:
                # Populate fields if it wasn't already done by JS
                self.answers.respondent_address_1 = selected_address.line_1
                self.answers.respondent_address_2 = selected_address.line_2
                self.answers.respondent_address_3 = selected_address.post_town
        """ # TODO (maybe)
        There is an edge case where a user with JS disabled selects an
        address from the API-supplied list (which populates the address fields
        within self.answers), but then goes back and selects a
        different address from the list. Upon returning to the form, the
        individual address fields will be populated, but upon submission the
        existing address fields are not overwritten by the new value from the
        list. The view does not know whether JS is enabled when it sets the
        initial address field values so it provides the user-submitted values,
        which may have been edited from the API-supplied values. Possible
        solutions are:
        - Test to see whether the UDPRN has changed but address_1 has not
        - Split this into an additional step:
            1. postcode -> 2. select property/not in list -> 3. confirm address
          (would still have to check for a change in UDPRN before overwriting address?)
        - hide address selector if address fields are populated
        """


class Email(abstract_views.SingleQuestion):
    title = "Your email address"
    type_ = abstract_views.QuestionType.Text
    question = "Enter your email address"
    next = "ContactPhone"
    percent_complete = COMPLETE_TRAIL + 30

    @staticmethod
    def validate_answer(field):
        validate_email(field)


class ContactPhone(abstract_views.Question):
    title = "Your phone number"
    form_class = questionnaire_forms.RespondentPhone
    template_name = "questionnaire/respondent_phone.html"
    percent_complete = COMPLETE_TRAIL + 35

    def get_next(self):
        if self.answers.is_occupant:
            return "PropertyPostcode"
        else:
            return "OccupantName"


class OccupantName(abstract_views.Question):
    title = "Occupant name"
    template_name = "questionnaire/occupant_name.html"
    form_class = questionnaire_forms.OccupantName
    next = "PropertyPostcode"
    percent_complete = COMPLETE_TRAIL + 40


class PropertyPostcode(abstract_views.SingleQuestion):
    title = "Property postcode"
    type_ = abstract_views.QuestionType.Text
    question = "Enter the property postcode"
    supplementary = "This is the postcode for the property."
    icon = "house"
    next = "PropertyAddress"
    percent_complete = COMPLETE_TRAIL + 45

    def sanitise_answer(self, data):
        data = postcodes.normalise(data)
        return data

    @staticmethod
    def validate_answer(value):
        if not postcodes.validate_household_postcode(value):
            raise ValidationError(
                "This does not appear to be a valid UK domestic postcode. Please check and re-enter"
            )
        postcode = postcodes.normalise(value)
        if postcode[0:2] != "PL":
            raise ValidationError(
                "This tool is only available to properties within the Plymouth Council area."
            )


class PropertyAddress(abstract_views.Question):
    title = "Address"
    form_class = questionnaire_forms.PropertyAddress
    template_name = "questionnaire/property_address.html"
    percent_complete = COMPLETE_TRAIL + 50
    prefilled_addresses = {}

    # Perform the API call to provide the choices for the address
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            self.prefilled_addresses = {
                address.id: address
                for address in get_addresses_for_postcode(
                    self.answers.property_postcode
                )
            }
        except ValueError:
            pass

        kwargs["prefilled_addresses"] = self.prefilled_addresses
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["property_postcode"] = self.answers.property_postcode
        context["all_postcode_addresses"] = {
            key: {
                "address1": address.address_1,
                "address2": address.address_2,
                "address3": address.address_3,
            }
            for key, address in self.prefilled_addresses.items()
        }
        return context

    def pre_save(self):
        if (
            self.answers.property_udprn
            and int(self.answers.property_udprn) in self.prefilled_addresses
        ):
            selected_address = self.prefilled_addresses[
                int(self.answers.property_udprn)
            ]
            self.answers.uprn = selected_address.uprn or None
            if not self.answers.property_address_1:
                # Populate fields if it wasn't already done by JS
                self.answers.property_address_1 = selected_address.line_1
                self.answers.property_address_2 = selected_address.line_2
                self.answers.property_address_3 = selected_address.line_3

        # TODO (maybe) same edge case as with RespondentAddress above.

        if self.answers.property_address_1 and self.answers.property_address_2:
            try:
                self.answers = services.prepopulate_from_parity(self.answers)
                self.answers.save()
            except Exception as e:
                logging.error("prepopulate_from_parity failed", e)

    def get_next(self):
        if self.answers.sap_score:
            return "Tenure"
        else:
            return "AddressUnknown"


class AddressUnknown(abstract_views.Question):
    icon = "house"
    title = "We do not have data about your property"
    answer_field = "respondent_comments"
    form_class = questionnaire_forms.PropertyMeasuresSummary
    template_name = "questionnaire/address_unknown.html"
    percent_complete = COMPLETE_TRAIL + 75

    next = "ThankYou"


class ThankYou(abstract_views.NoQuestion):
    icon = "house"
    template_name = "questionnaire/thank_you.html"
    percent_complete = COMPLETE_TRAIL + 100

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        services.close_questionnaire(self.answers)
        return context

    def get_prev_url(self):
        return None


class Tenure(abstract_views.SingleQuestion):
    title = "Property ownership"
    type_ = abstract_views.QuestionType.Choices
    question = "What is the tenure of the property - how is it occupied?"
    choices = enums.Tenure.choices
    icon = "house"
    percent_complete = COMPLETE_TRAIL + 53
    next = "Consents"


class Consents(abstract_views.Question):
    title = "Your consent to our use of your data"
    template_name = "questionnaire/consents.html"
    form_class = questionnaire_forms.Consents
    next = "PropertyMeasuresSummary"
    percent_complete = COMPLETE_TRAIL + 55


class PropertyMeasuresSummary(abstract_views.Question):
    title = "Summary of property measures"
    form_class = questionnaire_forms.PropertyMeasuresSummary
    answer_field = "respondent_comments"
    template_name = "questionnaire/property_summary.html"
    next = "Occupants"
    percent_complete = COMPLETE_TRAIL + 60

    def get_context_data(self, *args, **kwargs):
        a = self.answers
        context = super().get_context_data(*args, **kwargs)

        context["property_data"] = {
            "type": f"{a.get_property_type_display()}",
            "attachment": f"{a.get_property_attachment_display()}",
            "construction_years": f"{a.get_property_construction_years_display()}",
            "wall_construction": f"{a.get_wall_construction_display()}",
            "walls_insulation": f"{a.get_walls_insulation_display()}",
            "roof_construction": f"{a.get_roof_construction_display()}",
            "roof_insulation": f"{a.get_roof_insulation_display()}",
            "floor_construction": f"{a.get_floor_construction_display()}",
            "floor_insulation": f"{a.get_floor_insulation_display()}",
            "glazing": f"{a.get_glazing_display()}",
            "heating": f"{a.get_heating_display()}",
            "main_fuel": f"{a.get_main_fuel_display()}",
            "boiler_efficiency": f"{a.get_boiler_efficiency_display()}",
            "controls_adequacy": f"{a.get_controls_adequacy_display()}",
            "realistic_fuel_bill": f"{a.realistic_fuel_bill}",
            "sap_band": f"{a.sap_band}",
        }

        return context


class Occupants(abstract_views.Question):
    template_name = "questionnaire/occupants.html"
    title = "The Household"
    next = "HouseholdIncome"
    percent_complete = COMPLETE_TRAIL + 65
    form_class = questionnaire_forms.Occupants


class HouseholdIncome(abstract_views.SingleQuestion):
    answer_field = "total_income"
    question = "Is the household income less than £31,000 before tax?"
    note = (
        "Household income means the combined income of everyone living in the property."
    )
    title = "Gross household income"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.IncomeIsUnderThreshold.choices
    percent_complete = COMPLETE_TRAIL + 70

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.total_income == enums.IncomeIsUnderThreshold.YES.value:
            self.answers.take_home = enums.IncomeIsUnderThreshold.YES.value
            self.answers.disability_benefits = None
            self.answers.child_benefit = None
            self.answers.child_benefit_threshold = None
            self.answers.income_lt_child_benefit_threshold = None

    def get_next(self):
        if self.answers.total_income == enums.IncomeIsUnderThreshold.YES.value:
            return "Vulnerabilities"
        else:
            return "HouseholdTakeHomeIncome"


class HouseholdTakeHomeIncome(abstract_views.SingleQuestion):
    answer_field = "take_home"
    question = (
        "Is the household income less than £31,000 after tax, mortgage/rent, "
        " and energy bills?"
    )
    note = (
        "Household income means the combined income of everyone living in the property."
    )
    title = "Total household pay after costs"
    next = "DisabilityBenefits"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.IncomeIsUnderThreshold.choices
    percent_complete = COMPLETE_TRAIL + 75


class DisabilityBenefits(abstract_views.SingleQuestion):
    title = "Diability benefits"
    type_ = abstract_views.QuestionType.YesNo
    question = (
        "Does anybody living in the home receive any disability related benefits?"
    )
    note = (
        "This would include: Attendance Allowance, Carers Allowance, Disability Living Allowance, "
        "Income Related ESA, Personal Independence Payment, Armed Forces Independence Payment, "
        "Industrial Injuries Disablement Benefit, Mobility Supplement or Severe Disablement Allowance."
    )
    percent_complete = COMPLETE_TRAIL + 80

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.disability_benefits:
            self.answers.child_benefit = None
            self.answers.child_benefit_number_elsewhere = None
            self.answers.child_benefit_claimant_type = None
            self.answers.child_benefit_summary = None
            self.answers.child_benefit_threshold = None
            self.answers.income_lt_child_benefit_threshold = None

    def get_next(self):
        if self.answers.disability_benefits:
            return "Vulnerabilities"
        else:
            return "ChildBenefit"


class ChildBenefit(abstract_views.SingleQuestion):
    title = "Child benefit"
    type_ = abstract_views.QuestionType.YesNo
    question = "Does anybody living in the home receive Child Benefit?"
    percent_complete = COMPLETE_TRAIL + 83

    def pre_save(self):
        # Set the benefit threshold dependent on the household composition
        if not self.answers.child_benefit:
            # Obliterate values from the etc.
            self.answers.child_benefit_threshold = None
            self.answers.income_lt_child_benefit_threshold = None

    def get_next(self):
        if self.answers.child_benefit:
            return "ChildBenefitNumber"
        else:
            return "Vulnerabilities"


class ChildBenefitNumber(abstract_views.SingleQuestion):
    title = "Child Benefit number"
    next = "ChildBenefitClaimantType"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.UpToFourOrMore.choices
    question = (
        "How many children do you claim child benefit for "
        "(whether living in the house or elsewhere) "
        "or pay at least £21.80 per week of maintenance payments towards?"
    )
    percent_complete = COMPLETE_TRAIL + 85


class ChildBenefitClaimantType(abstract_views.SingleQuestion):
    title = "Type of Child Benefit claimant"
    next = "ChildBenefitSummary"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.ChildBenefitClaimantType.choices
    question = (
        "Thinking of the adult that receives Child Benefit and lives within "
        "the house.<br>"
        "Is the adult single and living with other adults or living with a "
        "partner (ie. someone they are married to, civil partnered with or "
        "cohabitating as a couple)?"
    )
    note = (
        "Is the adult single and living with other adults, or living with a " "partner?"
    )
    percent_complete = COMPLETE_TRAIL + 87


class ChildBenefitSummary(abstract_views.Question):
    template_name = "questionnaire/child_benefit_summary.html"
    next = "IncomeLtChildBenefitThreshold"
    form_class = questionnaire_forms.ChildBenefitSummary
    percent_complete = COMPLETE_TRAIL + 88

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(
            {
                "answers": self.answers,
            }
        )
        return context

    def get_initial(self):
        data = super().get_initial()
        if self.answers.child_benefit_eligibility_complete is not None:
            data["confirm_or_amend"] = (
                "YES" if self.answers.child_benefit_eligibility_complete else "NO"
            )
        return data

    def pre_save(self):
        # Catch a request to go back & edit
        if self.answers.confirm_or_amend == "AMEND":
            self.answers.child_benefit_eligibility_complete = None
            self.next = "ChildBenefit"
        else:
            self.answers.child_benefit_eligibility_complete = (
                self.answers.confirm_or_amend == "YES"
            )


class IncomeLtChildBenefitThreshold(abstract_views.SingleQuestion):
    """IncomeLtChildBenefitThreshold.

    The income threshold depends on the type of claimant and number of
    children/qualifying young persons:

        see: utils.get_child_benefit_threshold

    https://www.legislation.gov.uk/uksi/2018/1183/schedule/2/made

    """

    title = "Income in relation to child benefit threshold"
    next = "Vulnerabilities"
    percent_complete = COMPLETE_TRAIL + 90
    type_ = abstract_views.QuestionType.YesNo

    def get_question(self):
        assert self.answers.child_benefit_threshold is not None

        if (
            self.answers.child_benefit_claimant_type
            == enums.ChildBenefitClaimantType.SINGLE
        ):
            return (
                "Is the income of the person receiving child benefit less than "
                f"£{self.answers.child_benefit_threshold:,} "
                "before tax?"
            )
        elif (
            self.answers.child_benefit_claimant_type
            == enums.ChildBenefitClaimantType.JOINT
        ):
            return (
                "Is the income of the couple (the person receiving child "
                "benefit and their partner) less than "
                f"£{self.answers.child_benefit_threshold:,} "
                "before tax?"
            )

    def prereq(self):
        self.answers.child_benefit_threshold = utils.get_child_benefit_threshold(
            self.answers
        )


class Vulnerabilities(abstract_views.Question):
    template_name = "questionnaire/vulnerabilities.html"
    title = "Specific vulnerabilities of household members"
    next = "AnswersSummary"
    percent_complete = COMPLETE_TRAIL + 95
    form_class = questionnaire_forms.Vulnerabilities


class AnswersSummary(abstract_views.Question):
    type_ = abstract_views.QuestionType.Choices
    choices = enums.HowDidYouHearAboutPEC.choices
    form_class = questionnaire_forms.AnswersSummary
    title = "Summary of your answers"
    percent_complete = COMPLETE_TRAIL + 98
    template_name = "questionnaire/answers_summary.html"

    def get_context_data(self, *args, **kwargs):
        a = self.answers
        context = super().get_context_data(*args, **kwargs)

        context["user_data"] = {
            "full_name": f"{a.first_name} {a.last_name}",
            "email": a.email,
            "respondent_role": a.get_respondent_role_display(),
            "respondent_role_other": a.respondent_role_other,
            "phone": a.contact_phone,
            "mobile": a.contact_mobile,
            "property_address": f"{a.property_address_1} \
            {a.property_address_2} {a.property_address_3} \
            {a.property_postcode}",
            "adults": a.adults,
            "children": a.children,
            "total_income": a.get_total_income_display(),
            "take_home_lt_31k_confirmation": a.take_home_lt_31k_confirmation,
            "vulnerable_cariovascular": a.vulnerable_cariovascular,
            "vulnerable_respiratory": a.vulnerable_respiratory,
            "vulnerable_mental_health": a.vulnerable_mental_health,
            "vulnerable_cns": a.vulnerable_cns,
            "vulnerable_disability": a.vulnerable_disability,
            "vulnerable_age": a.vulnerable_age,
            "vulnerable_child_pregnancy": a.vulnerable_child_pregnancy,
            "disability_benefits": a.disability_benefits,
            "child_benefit": a.child_benefit,
            "child_benefit_number": a.get_child_benefit_number_display(),
            "child_benefit_claimant_type": a.get_child_benefit_claimant_type_display(),
        }

        if a.respondent_address_1 or a.respondent_address_2 or a.respondent_address_3:
            context["user_data"][
                "address"
            ] = f"{a.respondent_address_1} {a.respondent_address_2} {a.respondent_address_3} {a.respondent_postcode}"

        if a.occupant_first_name or a.occupant_last_name:
            context["user_data"][
                "occupant_name"
            ] = f"{a.occupant_first_name} {a.occupant_last_name}"

        return context

    def get_prev_url(self):
        return None

    def get_next(self):
        return "RecommendedMeasures"


class RecommendedMeasures(abstract_views.Question):
    template_name = "questionnaire/recommended_measures.html"
    title = "Recommendations for this property"
    percent_complete = COMPLETE_TRAIL + 100

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        services.close_questionnaire(self.answers)
        measures = utils.determine_recommended_measures(self.answers)
        for measure in measures:
            measure.disruption = utils.get_disruption(measure)
            measure.comfort_benefit = utils.get_comfort_benefit(measure)
            measure.bill_impact = utils.get_bill_impact(measure)

        context["measures"] = measures
        context["full_name"] = f"{self.answers.first_name} {self.answers.last_name}"
        context["rating"] = utils.get_overall_rating(self.answers)
        context["sap_rating"] = self.answers.sap_score
        context["property_rating"] = utils.get_property_rating(self.answers)
        context["income_rating"] = utils.get_income_rating(self.answers)
        return context

    # Due to closing questionnaire we also remove "Back to previous question" link
    def get_prev_url(self):
        return None


class ToleratedDisruption(abstract_views.SingleQuestion):
    title = "Disruption preference"
    question = "What level of disruption would be acceptable during home upgrade works?"
    type_ = abstract_views.QuestionType.Choices
    next = "StateOfRepair"

    def get_choices(self):
        # Only non-owners get to answer "I don't know"
        if self.answers.is_owner:
            return enums.ToleratedDisruption.choices[:-1]
        else:
            return enums.ToleratedDisruption.choices

    def get_note(self):
        if not self.answers.is_owner:
            return (
                "Please answer on behalf of the owner if you can, or select "
                "\"I don't know\" if you don't know the owner's motivations."
            )


class StateOfRepair(abstract_views.SingleQuestion):
    title = "State of repair"
    question = "What condition is the property currently in?"
    type_ = abstract_views.QuestionType.Choices
    next = "Motivations"

    def get_choices(self):
        # Only non-owners get to answer "I don't know"
        if self.answers.is_owner:
            return enums.StateOfRepair.choices[:-1]
        else:
            return enums.StateOfRepair.choices


class ContributionCapacity(abstract_views.SingleQuestion):
    title = "Your ability to contribute"
    type_ = abstract_views.QuestionType.Choices

    def get_question(self):
        if self.answers.is_owner:
            return (
                "Would you be willing to contribute towards a package of improvements "
                "to your property in order to get the best outcome for your home?"
            )
        else:
            return (
                "Would the owner be willing to contribute towards a package of "
                "improvements in order to get the best outcome for their property?"
            )

    def get_choices(self):
        # Only non-owners get to answer "I don't know"
        if self.answers.is_owner:
            return enums.ContributionCapacity.choices[:-1]
        else:
            return enums.ContributionCapacity.choices

    def get_note(self):
        if not self.answers.is_owner:
            return (
                "Please answer on behalf of the owner if you can, or select "
                "\"I don't know\" if you don't know the owner's ability and "
                "willingness to contribute."
            )

    def pre_save(self):
        # Set up the number of adults we want for the next step
        services.sync_household_adults(self.answers)

    def get_next(self):
        rating = utils.get_overall_rating(self.answers)
        if rating in [enums.RAYG.GREEN, enums.RAYG.YELLOW]:
            return "Adult1Name"
        else:
            return "NothingAtThisTime"


class Adult1Name(abstract_views.HouseholdAdultName):
    adult_number = 1


class Adult1Employment(abstract_views.HouseholdAdultEmployment):
    adult_number = 1


class Adult1EmploymentIncome(abstract_views.HouseholdAdultEmploymentIncome):
    adult_number = 1


class Adult1SelfEmploymentIncome(abstract_views.HouseholdAdultSelfEmploymentIncome):
    adult_number = 1


class Adult1WelfareBenefits(abstract_views.HouseholdAdultWelfareBenefits):
    adult_number = 1


class Adult1WelfareBenefitAmounts(abstract_views.HouseholdAdultWelfareBenefitAmounts):
    adult_number = 1


class Adult1PensionIncome(abstract_views.HouseholdAdultPensionIncome):
    adult_number = 1


class Adult1SavingsIncome(abstract_views.HouseholdAdultSavingsIncome):
    adult_number = 1


class Adult2Name(abstract_views.HouseholdAdultName):
    adult_number = 2


class Adult2Employment(abstract_views.HouseholdAdultEmployment):
    adult_number = 2


class Adult2EmploymentIncome(abstract_views.HouseholdAdultEmploymentIncome):
    adult_number = 2


class Adult2SelfEmploymentIncome(abstract_views.HouseholdAdultSelfEmploymentIncome):
    adult_number = 2


class Adult2WelfareBenefits(abstract_views.HouseholdAdultWelfareBenefits):
    adult_number = 2


class Adult2WelfareBenefitAmounts(abstract_views.HouseholdAdultWelfareBenefitAmounts):
    adult_number = 2


class Adult2PensionIncome(abstract_views.HouseholdAdultPensionIncome):
    adult_number = 2


class Adult2SavingsIncome(abstract_views.HouseholdAdultSavingsIncome):
    adult_number = 2


class Adult3Name(abstract_views.HouseholdAdultName):
    adult_number = 3


class Adult3Employment(abstract_views.HouseholdAdultEmployment):
    adult_number = 3


class Adult3EmploymentIncome(abstract_views.HouseholdAdultEmploymentIncome):
    adult_number = 3


class Adult3SelfEmploymentIncome(abstract_views.HouseholdAdultSelfEmploymentIncome):
    adult_number = 3


class Adult3WelfareBenefits(abstract_views.HouseholdAdultWelfareBenefits):
    adult_number = 3


class Adult3WelfareBenefitAmounts(abstract_views.HouseholdAdultWelfareBenefitAmounts):
    adult_number = 3


class Adult3PensionIncome(abstract_views.HouseholdAdultPensionIncome):
    adult_number = 3


class Adult3SavingsIncome(abstract_views.HouseholdAdultSavingsIncome):
    adult_number = 3


class Adult4Name(abstract_views.HouseholdAdultName):
    adult_number = 4


class Adult4Employment(abstract_views.HouseholdAdultEmployment):
    adult_number = 4


class Adult4EmploymentIncome(abstract_views.HouseholdAdultEmploymentIncome):
    adult_number = 4


class Adult4SelfEmploymentIncome(abstract_views.HouseholdAdultSelfEmploymentIncome):
    adult_number = 4


class Adult4WelfareBenefits(abstract_views.HouseholdAdultWelfareBenefits):
    adult_number = 4


class Adult4WelfareBenefitAmounts(abstract_views.HouseholdAdultWelfareBenefitAmounts):
    adult_number = 4


class Adult4PensionIncome(abstract_views.HouseholdAdultPensionIncome):
    adult_number = 4


class Adult4SavingsIncome(abstract_views.HouseholdAdultSavingsIncome):
    adult_number = 4


class HouseholdSummary(abstract_views.Question):
    template_name = "questionnaire/household_summary.html"
    next = "EligibilitySummary"
    form_class = questionnaire_forms.HouseholdSummary

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["calculated_income"] = utils.calculate_household_income(self.answers)
        context["adult_incomes"] = [
            {"name": adult.full_name, "income": utils.calculate_adult_income(adult)}
            for adult in self.answers.householdadult_set.all()
        ]
        return context

    def get_initial(self):
        data = super().get_initial()
        if self.answers.incomes_complete is not None:
            data["confirm_or_amend_income"] = (
                "YES" if self.answers.incomes_complete else "NO"
            )

        return data

    def pre_save(self):
        # Catch a request to go back & edit
        if self.answers.confirm_or_amend_income == "AMEND":
            self.answers.incomes_complete = None
            self.next = "Adult1Name"
        else:
            self.answers.incomes_complete = (
                self.answers.confirm_or_amend_income == "YES"
            )
            if utils.calculate_household_income(self.answers) < 31000:
                self.answers.take_home_lt_31k_confirmation = True


class EligibilitySummary(abstract_views.Question):
    template_name = "questionnaire/eligibility_summary.html"
    next = "Completed"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["property_rating"] = utils.get_property_rating(self.answers)
        context["financial_eligibility"] = utils.get_financial_eligibility(self.answers)
        context["incomes_complete"] = self.answers.incomes_complete
        return context

    def pre_save(self):
        services.close_questionnaire(self.answers)


class Completed(TemplateView):
    template_name = "questionnaire/completed.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        return context
