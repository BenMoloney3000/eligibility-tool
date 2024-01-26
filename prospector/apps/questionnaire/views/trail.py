import logging
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.views.generic.base import TemplateView

from . import abstract as abstract_views
from prospector.apis.data8 import get_for_postcode
from prospector.apps.parity.utils import get_addresses_for_postcode
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import forms as questionnaire_forms
from prospector.apps.questionnaire import services
from prospector.apps.questionnaire import utils
from prospector.dataformats import postcodes

logger = logging.getLogger(__name__)


SESSION_ANSWERS_ID = "questionnaire:answer_id"
SESSION_TRAIL_ID = "questionnaire:trail_id"


class Home(TemplateView):
    template_name = "questionnaire/home.html"


class Start(abstract_views.SingleQuestion):
    template_name = "questionnaire/start.html"
    type_ = abstract_views.QuestionType.YesNo
    title = "About this tool"
    answer_field = "terms_accepted_at"
    question = "Please confirm that you have read and accept our data privacy policy."
    next = "Consents"
    percent_complete = 0

    def pre_save(self):
        self.answers.terms_accepted_at = timezone.now()


class Consents(abstract_views.Question):
    title = "Your consent to our use of your data"
    template_name = "questionnaire/consents.html"
    form_class = questionnaire_forms.Consents
    next = "RespondentName"
    percent_complete = 3


class RespondentName(abstract_views.Question):
    title = "Your name"
    template_name = "questionnaire/respondent_name.html"
    next = "Email"
    percent_complete = 6
    form_class = questionnaire_forms.RespondentName


class Email(abstract_views.SingleQuestion):
    title = "Your email address"
    type_ = abstract_views.QuestionType.Text
    question = "Enter your email address"
    next = "ContactPhone"
    percent_complete = 9

    @staticmethod
    def validate_answer(field):
        validate_email(field)


class ContactPhone(abstract_views.Question):
    title = "Your phone number"
    form_class = questionnaire_forms.RespondentPhone
    template_name = "questionnaire/respondent_phone.html"
    percent_complete = 12
    next = "RespondentRole"


class RespondentRole(abstract_views.Question):
    title = "Your role"
    form_class = questionnaire_forms.RespondentRole
    template_name = "questionnaire/respondent_role.html"
    percent_complete = 15

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
        if self.answers.respondent_role in [
            enums.RespondentRole.TENANT.value,
            enums.RespondentRole.LANDLORD.value,
        ]:
            return "RespondentHasPermission"
        else:
            return "PropertyPostcode"


class RespondentHasPermission(abstract_views.SingleQuestion):
    title = "Householder consent"
    type_ = abstract_views.QuestionType.YesNo
    template_name = "questionnaire/consent_to_proceed.html"
    percent_complete = 18

    def get_question(self):
        # Wording of information depends on role:
        if self.answers.respondent_role == enums.RespondentRole.TENANT:
            return """You will need your landlord's consent to proceed with any retrofit works
                and your landlord may be required to contribute some of the cost of the work
                if you are eligible for funding."""
        elif self.answers.respondent_role == enums.RespondentRole.LANDLORD:
            return "You will need your tenant's consent to proceed with any retrofit works."

    def get_next(self):
        if self.answers.respondent_role == enums.RespondentRole.LANDLORD:
            return "CompanyName"
        else:
            return "PropertyPostcode"


class CompanyName(abstract_views.SingleQuestion):
    title = "Landlord company name"
    type_ = abstract_views.QuestionType.Text
    question = "What is your company name?"
    percent_complete = 21
    next = "RespondentPostcode"


class RespondentPostcode(abstract_views.SingleQuestion):
    title = "Your postcode"
    type_ = abstract_views.QuestionType.Text
    question = "Enter your postcode"
    supplementary = (
        "This is the postcode for your own address, not that of the property "
        "about which you're enquiring."
    )
    next = "RespondentAddress"
    percent_complete = 24

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
    next = "PropertiesLimit"
    percent_complete = 27
    prefilled_addresses = {}

    # Perform the API call to provide the choices for the address
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            self.prefilled_addresses = {
                address.udprn: address
                for address in get_for_postcode(self.answers.respondent_postcode)
            }
        except Exception:
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


class PropertiesLimit(abstract_views.SingleQuestion):
    title = "Properties limit"
    answer_field = "nmt4properties"
    type_ = abstract_views.QuestionType.YesNo
    question = "Do you confirm that you own no more than 4 properties?"
    percent_complete = 30
    next = "WillToContribute"


class WillToContribute(abstract_views.SingleQuestion):
    title = "Householder consent"
    answer_field = "willing_to_contribute"
    type_ = abstract_views.QuestionType.YesNo
    question = (
        "Would you be willing to contribute 33% of the cost toward retrofitting "
        "the home if your application to a grant scheme is successful?"
    )
    percent_complete = 33
    next = "PropertyPostcode"


class PropertyPostcode(abstract_views.SingleQuestion):
    title = "Property postcode"
    type_ = abstract_views.QuestionType.Text
    question = "Enter the property postcode"
    supplementary = "This is the postcode for the property."
    icon = "house"
    next = "PropertyAddress"
    percent_complete = 36

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
    percent_complete = 39
    prefilled_addresses = {}

    # Perform the API call to provide the choices for the address
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            self.prefilled_addresses = {
                property_object.id: property_object
                for property_object in get_addresses_for_postcode(
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
                "address1": property_object.address_1,
                "address2": property_object.address_2,
                "address3": property_object.address_3,
            }
            for key, property_object in self.prefilled_addresses.items()
        }
        return context

    def pre_save(self):
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
    percent_complete = 75
    next = "ThankYou"


class ThankYou(abstract_views.NoQuestion):
    icon = "house"
    template_name = "questionnaire/thank_you.html"
    percent_complete = 100

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
    percent_complete = 42
    next = "PropertyMeasuresSummary"


class PropertyMeasuresSummary(abstract_views.Question):
    title = "Summary of property measures"
    form_class = questionnaire_forms.PropertyMeasuresSummary
    answer_field = "respondent_comments"
    template_name = "questionnaire/property_summary.html"
    percent_complete = 45

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

    def get_next(self):
        if self.answers.respondent_role in [
            enums.RespondentRole.LANDLORD.value,
            enums.RespondentRole.OTHER.value,
        ]:
            return "OccupantName"
        else:
            return "Occupants"


class OccupantName(abstract_views.Question):
    title = "Occupant name"
    template_name = "questionnaire/occupant_name.html"
    form_class = questionnaire_forms.OccupantName
    next = "Occupants"
    percent_complete = 48


class Occupants(abstract_views.Question):
    template_name = "questionnaire/occupants.html"
    title = "The Household"
    next = "MeansTestedBenefits"
    percent_complete = 51
    form_class = questionnaire_forms.Occupants


class MeansTestedBenefits(abstract_views.SingleQuestion):
    type_ = abstract_views.QuestionType.YesNo
    title = "Means tested benefits"
    question = "Do you receive means tested benefits?"
    percent_complete = 54

    def get_next(self):
        if self.answers.means_tested_benefits:
            return "DisabilityBenefits"
        else:
            return "PastMeansTestedBenefits"


class PastMeansTestedBenefits(abstract_views.SingleQuestion):
    type_ = abstract_views.QuestionType.YesNo
    title = "Means tested benefits in the past"
    question = "Were you receiving means tested benefits in the last 18 months?"
    percent_complete = 57
    next = "DisabilityBenefits"


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
    percent_complete = 60
    next = "ChildBenefit"


class ChildBenefit(abstract_views.SingleQuestion):
    title = "Child benefit"
    type_ = abstract_views.QuestionType.YesNo
    question = "Do you receive child benefit?"
    percent_complete = 63

    def get_next(self):
        if self.answers.child_benefit:
            return "ChildBenefitClaimantType"
        else:
            return "VulnerabilitiesGeneral"


class ChildBenefitClaimantType(abstract_views.SingleQuestion):
    title = "Type of Child Benefit claimant"
    next = "ChildBenefitNumber"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.ChildBenefitClaimantType.choices
    question = "Are you a single claimant or member of a couple?"
    note = (
        "Is the adult single and living with other adults, or living with a " "partner?"
    )
    percent_complete = 66


class ChildBenefitNumber(abstract_views.SingleQuestion):
    title = "Child Benefit number"
    next = "VulnerabilitiesGeneral"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.OneToFiveOrMore.choices
    question = (
        "How many children or qualifying young "
        "people do you receive child benefit for?"
    )
    percent_complete = 69


class VulnerabilitiesGeneral(abstract_views.SingleQuestion):
    type_ = abstract_views.QuestionType.YesNo
    title = "Vulnerability to the cold"
    question = "Vulnerability to the cold"
    supplementary = (
        "Does your household fall under any of the following categories?"
        "<ul><li>Household living with cardiovascular conditions</li>"
        "<li> Household living with respiratory conditions, "
        "in particular, chronic obstructive pulmonary disease "
        "(COPD) and childhood asthma</li>"
        "<li>Household living with mental health conditions</li>"
        "<li>Household living with disabilities or limited mobility</li>"
        "<li>Household with an older person (65 and older)</li>"
        "<li>Household with young children (from  new-born to school age)</li>"
        "<li>Household living with immunosuppression</li>"
        "<li>Household with a pregnant woman</li>"
        "<li>Household living with any other conditions "
        "causing medical vulnerability to the cold</li></ul>"
    )
    percent_complete = 72

    def get_next(self):
        if self.answers.vulnerabilities_general:
            return "Vulnerabilities"
        else:
            return "HouseholdIncome"


class Vulnerabilities(abstract_views.Question):
    template_name = "questionnaire/vulnerabilities.html"
    title = "Specific vulnerabilities of household members"
    next = "HouseholdIncome"
    percent_complete = 75
    form_class = questionnaire_forms.Vulnerabilities


class HouseholdIncome(abstract_views.SingleQuestion):
    type_ = abstract_views.QuestionType.Text
    question = "Total household income"
    supplementary = (
        "What is your total household income before tax "
        "including any means tested benefits?"
    )
    title = "Household income"
    icon = "house"
    next = "HousingCosts"
    percent_complete = 78

    def sanitise_answer(self, data):
        data = re.sub(",", "", data)
        data = re.sub("£", "", data)
        return data

    @staticmethod
    def validate_answer(data):
        for character in data:
            if character not in "£," and not character.isdigit():
                raise ValidationError(
                    "It seems that you used one or more invalid characters."
                    " Please enter a value represented by an integer number."
                )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(
            {
                "answers": self.answers,
            }
        )
        return context


class HousingCosts(abstract_views.SingleQuestion):
    type_ = abstract_views.QuestionType.Text
    question = "What are your housing costs?"
    title = "Housing costs"
    icon = "house"
    next = "CouncilTaxReduction"
    percent_complete = 81

    def get_supplementary(self):
        if self.answers.respondent_role in [
            enums.RespondentRole.OTHER.value,
            enums.RespondentRole.LANDLORD.value,
        ]:
            return "Please tell us how much the household pays in rent each month."
        else:
            return (
                "Please tell us how much you pay each month for your rent or mortgage."
            )

    def sanitise_answer(self, data):
        data = re.sub(",", "", data)
        data = re.sub("£", "", data)
        return data

    @staticmethod
    def validate_answer(data):
        for character in data:
            if character not in "£," and not character.isdigit():
                raise ValidationError(
                    "It seems that you used one or more invalid characters."
                    " Please enter a value represented by an integer number."
                )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(
            {
                "answers": self.answers,
            }
        )
        return context


class CouncilTaxReduction(abstract_views.SingleQuestion):
    type_ = abstract_views.QuestionType.YesNo
    title = "Council Tax Reduction"
    question = "Is the household entitled to a Council Tax reduction on the grounds of low income?"
    next = "FreeSchoolMealsEligibility"
    percent_complete = 86


class FreeSchoolMealsEligibility(abstract_views.SingleQuestion):
    type_ = abstract_views.QuestionType.YesNo
    title = "Free school meals"
    question = (
        "Are any children living in the household eligible "
        "for free school meals due to low income?"
    )
    next = "EnergyAdvices"
    percent_complete = 90


class EnergyAdvices(abstract_views.Question):
    title = "Energy advice"
    template_name = "questionnaire/energy_advice.html"
    form_class = questionnaire_forms.EnergyAdvices
    next = "AnswersSummary"
    percent_complete = 93


class AnswersSummary(abstract_views.Question):
    type_ = abstract_views.QuestionType.Choices
    choices = enums.HowDidYouHearAboutPEC.choices
    form_class = questionnaire_forms.AnswersSummary
    title = "Summary of your answers"
    percent_complete = 96
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
            "seniors": a.seniors,
            "household_income": a.household_income,
            "housing_costs": a.housing_costs,
            "council_tax_reduction": a.council_tax_reduction,
            "vulnerable_cariovascular": a.vulnerable_cariovascular,
            "vulnerable_respiratory": a.vulnerable_respiratory,
            "vulnerable_mental_health": a.vulnerable_mental_health,
            "vulnerable_disability": a.vulnerable_disability,
            "vulnerable_age": a.vulnerable_age,
            "vulnerable_children": a.vulnerable_children,
            "vulnerable_immunosuppression": a.vulnerable_immunosuppression,
            "vulnerable_pregnancy": a.vulnerable_pregnancy,
            "vulnerable_comments": a.vulnerable_comments or None,
            "means_tested_benefits": a.means_tested_benefits,
            "past_means_tested_benefits": a.past_means_tested_benefits,
            "disability_benefits": a.disability_benefits,
            "child_benefit": a.child_benefit,
            "child_benefit_number": a.get_child_benefit_number_display(),
            "child_benefit_claimant_type": a.get_child_benefit_claimant_type_display(),
            "free_school_meals_eligibility": a.free_school_meals_eligibility,
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
    template_name = "questionnaire/final_recommendations.html"
    title = "Recommendations for this property"
    percent_complete = 100

    def determine_recommended_measures(self):
        measures = []
        if self.answers.is_cavity_wall_insulation_recommended:
            measures.append(enums.PossibleMeasures.CAVITY_WALL_INSULATION)
        if self.answers.is_solid_wall_insulation_recommended:
            measures.append(enums.PossibleMeasures.SOLID_WALL_INSULATION)
        if self.answers.is_underfloor_insulation_recommended:
            measures.append(enums.PossibleMeasures.UNDERFLOOR_INSULATION)
        if self.answers.is_loft_insulation_recommended:
            measures.append(enums.PossibleMeasures.LOFT_INSULATION)
        if self.answers.is_rir_insulation_recommended:
            measures.append(enums.PossibleMeasures.RIR_INSULATION)
        if self.answers.is_boiler_upgrade_recommended:
            measures.append(enums.PossibleMeasures.BOILER_UPGRADE)
        if self.answers.is_heatpump_installation_recommended:
            measures.append(enums.PossibleMeasures.HEAT_PUMP_INSTALLATION)
        if self.answers.is_solar_pv_installation_recommended:
            measures.append(enums.PossibleMeasures.SOLAR_PV_INSTALLATION)
        if len(measures) == 0:
            return None
        return measures

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        services.close_questionnaire(self.answers)
        measures = self.determine_recommended_measures()
        if measures:
            for measure in measures:
                measure.disruption = utils.get_disruption(measure)
                measure.comfort_benefit = utils.get_comfort_benefit(measure)
                measure.bill_impact = utils.get_bill_impact(measure)

        context["measures"] = measures
        context["full_name"] = f"{self.answers.first_name} {self.answers.last_name}"
        context["not_in_mains_gas"] = self.answers.is_property_not_heated_by_mains_gas
        context["any_scheme_eligible"] = self.answers.is_any_scheme_eligible
        context["bus_eligibility"] = self.answers.is_bus_eligible
        context["eco4_eligibility"] = self.answers.is_eco4_eligible
        context["eco4flex_eligibility"] = self.answers.is_eco4_flex_eligible
        context["eco4_condition_1"] = self.answers.if_off_mains_gas_and_given_sap_score
        context["eco4_condition_2"] = self.answers.sap_band == enums.EfficiencyBand.D
        context["cfw_eligibility"] = self.answers.is_connected_for_warmth_eligible
        context["gbis_eligibility"] = self.answers.is_gbis_eligible
        context["hug2_eligibility"] = self.answers.is_hug2_eligible
        return context

    # Due to closing questionnaire we also remove "Back to previous question" link
    def get_prev_url(self):
        return None
