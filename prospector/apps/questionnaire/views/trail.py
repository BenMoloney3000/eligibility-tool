import logging

from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.views.generic.base import TemplateView

from . import abstract as abstract_views
from prospector.apis import epc
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import forms as questionnaire_forms
from prospector.apps.questionnaire import selectors
from prospector.apps.questionnaire import services
from prospector.apps.questionnaire import utils
from prospector.dataformats import postcodes


logger = logging.getLogger(__name__)


SESSION_ANSWERS_ID = "questionnaire:answer_id"
SESSION_TRAIL_ID = "questionnaire:trail_id"
POSTCODE_CACHE = caches["postcodes"]


class Start(abstract_views.SingleQuestion):
    template_name = "questionnaire/start.html"
    type_ = abstract_views.QuestionType.YesNo
    title = "About this tool"
    answer_field = "terms_accepted_at"
    question = "Please confirm that you have read and accept our data privacy policy."
    next = "RespondentName"

    def pre_save(self):
        self.answers.terms_accepted_at = timezone.now()


class RespondentName(abstract_views.Question):
    title = "Your name"
    template_name = "questionnaire/respondent_name.html"
    next = "RespondentRole"
    form_class = questionnaire_forms.RespondentName


class RespondentRole(abstract_views.Question):
    title = "Your role"
    form_class = questionnaire_forms.RespondentRole
    template_name = "questionnaire/respondent_role.html"

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

    def sanitise_answer(self, data):
        data = postcodes.normalise(data)
        return data

    @staticmethod
    def validate_answer(value):
        if not postcodes.validate_household_postcode(value):
            raise ValidationError(
                "This does not appear to be a valid UK domestic postcode. Please check and re-enter"
            )


class RespondentAddress(abstract_views.Question, abstract_views.PostcodeCacherMixin):
    title = "Your address"
    form_class = questionnaire_forms.RespondentAddress
    template_name = "questionnaire/respondent_address.html"
    next = "Email"
    prefilled_addresses = {}

    # Perform the API call to provide the choices for the address
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            self.prefilled_addresses = {
                address.udprn: address
                for address in self.get_postcode(self.answers.respondent_postcode)
            }
        except ValueError:
            pass

        kwargs["prefilled_addresses"] = self.prefilled_addresses
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["postcode"] = self.answers.respondent_postcode
        context["all_postcode_addresses"] = self.prefilled_addresses
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

    @staticmethod
    def validate_answer(field):
        validate_email(field)


class ContactPhone(abstract_views.Question):
    title = "Your phone number"
    form_class = questionnaire_forms.RespondentPhone
    template_name = "questionnaire/respondent_phone.html"

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


class PropertyPostcode(abstract_views.SingleQuestion):
    title = "Property postcode"
    type_ = abstract_views.QuestionType.Text
    question = "Enter the property postcode"
    supplementary = (
        "This is the postcode for the property about which you're enquiring."
    )
    next = "PropertyAddress"

    def sanitise_answer(self, data):
        data = postcodes.normalise(data)
        return data

    @staticmethod
    def validate_answer(value):
        if not postcodes.validate_household_postcode(value):
            raise ValidationError(
                "This does not appear to be a valid UK domestic postcode. Please check and re-enter"
            )
        if value[0:2] != "PL":
            raise ValidationError(
                "This tool is only available to properties within the Plymouth Council area."
            )


class PropertyAddress(abstract_views.Question, abstract_views.PostcodeCacherMixin):
    title = "Property address"
    form_class = questionnaire_forms.PropertyAddress
    template_name = "questionnaire/property_address.html"
    next = "PropertyOwnership"
    prefilled_addresses = {}

    # Perform the API call to provide the choices for the address
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            # Cache these in the session to avoid another call on POST
            self.prefilled_addresses = {
                address.udprn: address
                for address in self.get_postcode(self.answers.property_postcode)
            }
        except ValueError:
            pass

        kwargs["prefilled_addresses"] = self.prefilled_addresses
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["property_postcode"] = self.answers.property_postcode
        context["all_postcode_addresses"] = self.prefilled_addresses
        return context

    def pre_save(self):
        if (
            self.answers.property_udprn
            and int(self.answers.property_udprn) in self.prefilled_addresses
        ):
            selected_address = self.prefilled_addresses[
                int(self.answers.property_udprn)
            ]
            self.answers.uprn = selected_address.uprn
            if not self.answers.property_address_1:
                # Populate fields if it wasn't already done by JS
                self.answers.property_address_1 = selected_address.line_1
                self.answers.property_address_2 = selected_address.line_2
                self.answers.property_address_3 = selected_address.line_3

        # TODO (maybe) same edge case as with RespondentAddress above.


class PropertyOwnership(abstract_views.SingleQuestion):
    title = "Property ownership"
    type_ = abstract_views.QuestionType.Choices
    question = "What is the tenure of the property - how is it occupied?"
    choices = enums.PropertyOwnership.choices
    next = "Consents"


class Consents(abstract_views.Question):
    title = "Your consent to our use of your data"
    question = "Please confirm how we can use your data"
    template_name = "questionnaire/consents.html"
    form_class = questionnaire_forms.Consents
    next = "SelectEPC"


class SelectEPC(abstract_views.Question):
    title = "Energy Performance Certificate (EPC)"
    template_name = "questionnaire/select_epc.html"
    form_class = questionnaire_forms.SelectEPC
    candidate_epcs = {}

    def get_form_kwargs(self):
        """Pass the possible EPCs into the form."""
        kwargs = super().get_form_kwargs()
        kwargs["candidate_epcs"] = self.candidate_epcs
        return kwargs

    def prereq(self):
        try:
            postcode_epcs = epc.get_for_postcode(self.answers.property_postcode)

            # Try to reduce the possible EPCs by UPRN
            # (can only filter out anything with a different EPC)
            # TODO could be some attempt to match the (full) address itself but it will
            # require a lot of experimentation for possibly not much benefit.
            if self.answers.uprn:
                postcode_epcs = [
                    epc
                    for epc in postcode_epcs
                    if epc.uprn == "" or epc.uprn == str(self.answers.uprn)
                ]
                # At this point anything with a UPRN will be our UPRN, move
                # that/them to the top of the list
                postcode_epcs.sort(reverse=True, key=lambda x: bool(x.uprn))
            self.candidate_epcs = {epc.id: epc for epc in postcode_epcs}
        except ValueError:
            pass

        if len(self.candidate_epcs) == 0:
            # No valid EPC. Continue.
            return self.redirect()

    def pre_save(self):
        # If we selected an EPC, this is where we interrogate its data to
        # pre-populate all the property energy performance questions
        if self.answers.selected_epc:
            selected_epc = self.candidate_epcs[self.answers.selected_epc]
            self.answers = services.prepopulate_from_epc(self.answers, selected_epc)
            self.answers.save()

    def get_next(self):
        # If we selected an EPC we show the data we've inferred, otherwise we
        # crack on and get the data.
        if self.answers.selected_epc:
            return "InferredData"
        else:
            return "PropertyType"


class InferredData(abstract_views.Question):
    title = "What we think about your property"
    template_name = "questionnaire/inferred_data.html"
    form_class = questionnaire_forms.InferredData
    next = "PropertyType"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["answers"] = self.answers

        # Send in the enums
        if self.answers.property_type_orig:
            context["initial_type"] = enums.PropertyType(
                self.answers.property_type_orig
            ).label
            context["initial_form"] = enums.PropertyForm(
                self.answers.property_form_orig
            ).label

        context["type_inferences_complete"] = self.answers.type_inferences_complete()
        context["wall_inferences_complete"] = self.answers.wall_inferences_complete()
        context["floor_inferences_complete"] = self.answers.floor_inferences_complete()
        context["roof_inferences_complete"] = self.answers.roof_inferences_complete()
        context[
            "heating_inferences_complete"
        ] = self.answers.heating_inferences_complete()

        context["any_inferences_complete"] = (
            context["type_inferences_complete"]
            or context["wall_inferences_complete"]
            or context["floor_inferences_complete"]
            or context["roof_inferences_complete"]
            or context["heating_inferences_complete"]
        )

        return context

    def pre_save(self):
        # Anything the user doesn't want to correct should be populated from the
        # origin data. If it's not complete then they shouldn't be able to skip.
        if (
            self.answers.type_inferences_complete()
            and self.answers.will_correct_type is False
        ):
            self.answers = services.set_type_from_orig(self.answers)
        if (
            self.answers.wall_inferences_complete()
            and self.answers.will_correct_walls is False
        ):
            self.answers = services.set_walls_from_orig(self.answers)
        if (
            self.answers.roof_inferences_complete()
            and self.answers.will_correct_roof is False
        ):
            self.answers = services.set_roof_from_orig(self.answers)
        if (
            self.answers.floor_inferences_complete()
            and self.answers.will_correct_floor is False
        ):
            self.answers = services.set_floor_from_orig(self.answers)
        if (
            self.answers.heating_inferences_complete()
            and self.answers.will_correct_heating is False
        ):
            self.answers = services.set_heating_from_orig(self.answers)

    def get_next(self):
        if (
            not self.answers.type_inferences_complete()
            or self.answers.will_correct_type
        ):
            return "PropertyType"
        elif (
            not self.answers.wall_inferences_complete()
            or self.answers.will_correct_walls
        ):
            return "WallType"
        elif (
            not self.answers.floor_inferences_complete()
            or self.answers.will_correct_floor
        ):
            return "SuspendedFloor"
        elif (
            not self.answers.roof_inferences_complete()
            or self.answers.will_correct_roof
        ):
            return "UnheatedLoft"
        elif (
            not self.answers.heating_inferences_complete()
            or self.answers.will_correct_heating
        ):
            return "GasBoilerPresent"
        else:
            # Really unlikely!
            return "InConservationArea"


class PropertyType(abstract_views.Question):
    title = "Property type"
    question = "What type of property is this?"
    template_name = "questionnaire/property_type.html"
    form_class = questionnaire_forms.PropertyType
    next = "PropertyAgeBand"

    def get_initial(self):
        data = super().get_initial()
        if data.get("property_type"):
            data["data_correct"] = bool(
                data.get("property_type_orig")
                and data.get("property_form_orig")
                and data["property_type"] == data["property_type_orig"]
                and data["property_form"] == data["property_form_orig"]
            )
        return data

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # Send in the enums
        if self.answers.property_type_orig:
            context["initial_type"] = enums.PropertyType(
                self.answers.property_type_orig
            ).label
            context["initial_form"] = enums.PropertyForm(
                self.answers.property_form_orig
            ).label

        return context


class PropertyAgeBand(abstract_views.SinglePrePoppedQuestion):
    title = "Property age"
    question = "When was the property built?"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.PropertyAgeBand.choices

    def pre_save(self):
        # If we didn't get the likely wall type, infer from the age now.
        if not self.answers.wall_type_orig:
            self.answers.wall_type_orig = int(self.answers.property_age_band) < 1930

    def get_next(self):
        # We may have decided to skip ahead
        if (
            not self.answers.wall_inferences_complete()
            or self.answers.will_correct_walls
        ):
            # the most common situation - don't skip anything
            return "WallType"
        elif (
            not self.answers.floor_inferences_complete()
            or self.answers.will_correct_floor
        ):
            return "SuspendedFloor"
        elif (
            not self.answers.roof_inferences_complete()
            or self.answers.will_correct_roof
        ):
            return "UnheatedLoft"
        elif (
            not self.answers.heating_inferences_complete()
            or self.answers.will_correct_heating
        ):
            return "GasBoilerPresent"
        else:
            return "InConservationArea"


class WallType(abstract_views.SinglePrePoppedQuestion):
    title = "Wall type"
    question = "What type of outside walls does the property have?"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.WallType.choices
    note = (
        "If the property has more than one type of outside wall, choose the one "
        "that makes up the most of the external area."
    )
    next = "WallsInsulated"


class WallsInsulated(abstract_views.SinglePrePoppedQuestion):
    title = "Wall type"
    question = "Are the outside walls in this property insulated?"
    type_ = abstract_views.QuestionType.YesNo
    note = (
        "If only some of the outside walls are insulated, choose the option that "
        "applies to the largest external area."
    )

    def get_next(self):
        # We may have decided to skip ahead
        if (
            not self.answers.floor_inferences_complete()
            or self.answers.will_correct_floor
        ):
            # the most common situation - don't skip anything
            return "SuspendedFloor"
        elif (
            not self.answers.roof_inferences_complete()
            or self.answers.will_correct_roof
        ):
            return "UnheatedLoft"
        elif (
            not self.answers.heating_inferences_complete()
            or self.answers.will_correct_heating
        ):
            return "GasBoilerPresent"
        else:
            return "InConservationArea"


class SuspendedFloor(abstract_views.SinglePrePoppedQuestion):
    title = "Floor type"
    question = "Does the property have a suspended timber floor with a void underneath?"
    type_ = abstract_views.QuestionType.YesNo
    note = (
        "If the property has different types of floor, choose the option that applies "
        "to the largest floor area. If the property is a non-ground-floor flat, select 'No'."
    )

    def prereq(self):
        # We may have decided to skip this part
        if (
            self.answers.floor_inferences_complete()
            and self.answers.will_correct_floor is False
        ):
            return self.redirect("UnheatedLoft")

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if not self.answers.suspended_floor:
            self.answers.suspended_floor_insulated = None

    def get_next(self):
        if self.answers.suspended_floor:
            return "SuspendedFloorInsulated"
        else:
            # We may have decided to skip ahead
            if (
                not self.answers.roof_inferences_complete()
                or self.answers.will_correct_roof
            ):
                # the most common situation - don't skip anything
                return "UnheatedLoft"
            elif (
                not self.answers.heating_inferences_complete()
                or self.answers.will_correct_heating
            ):
                return "GasBoilerPresent"
            else:
                return "InConservationArea"


class SuspendedFloorInsulated(abstract_views.SinglePrePoppedQuestion):
    title = "Floor insulation"
    question = "Is the suspended timber floor insulated?"
    type_ = abstract_views.QuestionType.YesNo

    def get_next(self):
        # We may have decided to skip ahead
        if (
            not self.answers.roof_inferences_complete()
            or self.answers.will_correct_roof
        ):
            # the most common situation - don't skip anything
            return "UnheatedLoft"
        elif (
            not self.answers.heating_inferences_complete()
            or self.answers.will_correct_heating
        ):
            return "GasBoilerPresent"
        else:
            return "InConservationArea"


class UnheatedLoft(abstract_views.SinglePrePoppedQuestion):
    title = "Property roof"
    question = "Does the property have an unheated loft space directly above it?"
    type_ = abstract_views.QuestionType.YesNo
    note = "If the property is a non-top-floor flat, select 'No'."

    def prereq(self):
        # We may have decided to skip this part
        if (
            self.answers.roof_inferences_complete()
            and self.answers.will_correct_roof is False
        ):
            return self.redirect("GasBoilerPresent")

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.unheated_loft:
            self.answers.room_in_roof = None
            self.answers.rir_insulated = None
            self.answers.flat_roof = None
            self.answers.flat_roof_insulated = ""
        else:
            self.answers.roof_space_insulated = None

    def get_next(self):
        if self.answers.unheated_loft:
            return "RoofSpaceInsulated"
        else:
            return "RoomInRoof"


class RoomInRoof(abstract_views.SinglePrePoppedQuestion):
    title = "Room in roof"
    question = "Is there a room in the roof space of the property, as a loft conversion or otherwise?"
    type_ = abstract_views.QuestionType.YesNo

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.room_in_roof:
            self.answers.flat_roof = None
            self.answers.flat_roof_insulated = ""
        else:
            self.answers.rir_insulated = None

    def get_next(self):
        if self.answers.room_in_roof:
            return "RirInsulated"
        else:
            return "FlatRoof"


class RirInsulated(abstract_views.SinglePrePoppedQuestion):
    title = "Room in roof insulation"
    question = "Has the room in the roof space been well insulated?"
    type_ = abstract_views.QuestionType.YesNo

    def get_next(self):
        # We may have decided to skip ahead
        if (
            not self.answers.heating_inferences_complete()
            or self.answers.will_correct_heating
        ):
            # the most common situation - don't skip anything
            return "GasBoilerPresent"
        else:
            return "InConservationArea"


class RoofSpaceInsulated(abstract_views.SinglePrePoppedQuestion):
    title = "Loft insulation"
    question = "Has the unheated loft space been well insulated?"
    type_ = abstract_views.QuestionType.YesNo
    note = "By 'well insulated' we mean with at least 250mm of mineral wool, or equivalent."

    def get_next(self):
        # We may have decided to skip ahead
        if (
            not self.answers.heating_inferences_complete()
            or self.answers.will_correct_heating
        ):
            # the most common situation - don't skip anything
            return "GasBoilerPresent"
        else:
            return "InConservationArea"


class FlatRoof(abstract_views.SinglePrePoppedQuestion):
    title = "Flat roof"
    question = "Does the property have a flat roof?"
    type_ = abstract_views.QuestionType.YesNo
    note = (
        "If the property has different roof types, choose the answer that applies "
        "to the largest roof area."
    )

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if not self.answers.flat_roof:
            self.answers.flat_roof_insulated = ""

    def get_next(self):
        if self.answers.flat_roof:
            return "FlatRoofInsulated"
        else:
            # We may have decided to skip ahead
            if (
                not self.answers.heating_inferences_complete()
                or self.answers.will_correct_heating
            ):
                # the most common situation - don't skip anything
                return "GasBoilerPresent"
            else:
                return "InConservationArea"


class FlatRoofInsulated(abstract_views.SingleQuestion):
    title = "Flat roof type"
    question = "Is your flat roof well insulated?"
    type_ = abstract_views.QuestionType.Choices
    next = "GasBoilerPresent"
    choices = enums.InsulationConfidence.choices

    def get_next(self):
        # We may have decided to skip ahead
        if (
            not self.answers.heating_inferences_complete()
            or self.answers.will_correct_heating
        ):
            # the most common situation - don't skip anything
            return "GasBoilerPresent"
        else:
            return "InConservationArea"


class GasBoilerPresent(abstract_views.SinglePrePoppedQuestion):
    title = "Gas boiler"
    question = "Does the property have a central heating system with a boiler running off mains gas?"
    type_ = abstract_views.QuestionType.YesNo

    def prereq(self):
        # We may have decided to skip this part (unlikely that we had the option!)
        if (
            self.answers.heating_inferences_complete()
            and self.answers.will_correct_heating is False
        ):
            return self.redirect("InConservationArea")

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.gas_boiler_present:
            self.answers.other_heating_present = None
            self.answers.other_heating_fuel = ""
            self.answers.storage_heaters_present = None
            self.answers.hhrshs_present = None
            self.answers.on_mains_gas = None
            self.answers.heat_pump_present = None
        else:
            self.answers.gas_boiler_age = ""
            self.answers.gas_boiler_broken = None

    def get_next(self):
        if self.answers.gas_boiler_present:
            return "HwtPresent"
        else:
            return "OnMainsGas"


class OnMainsGas(abstract_views.SinglePrePoppedQuestion):
    title = "Mains gas"
    question = "Is the property connected to the mains gas network?"
    type_ = abstract_views.QuestionType.YesNo
    next = "OtherHeatingPresent"


class OtherHeatingPresent(abstract_views.SinglePrePoppedQuestion):
    title = "Other central heating system"
    question = "Does the property have a non-gas central heating system?"
    type_ = abstract_views.QuestionType.YesNo

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.other_heating_present:
            self.answers.storage_heaters_present = None
            self.answers.hhrshs_present = None
        else:
            self.answers.hwt_present = None
            self.answers.other_heating_fuel = ""

    def get_next(self):
        if self.answers.other_heating_present:
            return "HwtPresent"
        else:
            return "StorageHeatersPresent"


class HwtPresent(abstract_views.SingleQuestion):
    title = "Hot water tank"
    question = "Does the property have a hot water tank?"
    type_ = abstract_views.QuestionType.YesNo

    def get_next(self):
        if self.answers.gas_boiler_present:
            return "GasBoilerAge"
        else:
            return "HeatPumpPresent"


class HeatPumpPresent(abstract_views.SinglePrePoppedQuestion):
    title = "Heat pump"
    question = "Is the heating system powered by a heat pump?"
    type_ = abstract_views.QuestionType.YesNo

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.heat_pump_present:
            self.answers.other_heating_fuel = None

    def get_next(self):
        if self.answers.heat_pump_present:
            return "InConservationArea"
        else:
            return "OtherHeatingFuel"


class OtherHeatingFuel(abstract_views.SinglePrePoppedQuestion):
    title = "Heating fuel source"
    question = "What fuel does the central heating system run on?"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.NonGasFuel.choices
    next = "InConservationArea"


class GasBoilerAge(abstract_views.SingleQuestion):
    title = "Boiler age"
    question = "When was the current boiler installed?"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.BoilerAgeBand.choices
    next = "GasBoilerBroken"


class GasBoilerBroken(abstract_views.SingleQuestion):
    title = "Boiler condition"
    question = "Is the gas boiler currently broken?"
    type_ = abstract_views.QuestionType.YesNo
    next = "HeatingControls"


class HeatingControls(abstract_views.Question):
    title = "Heating controls"
    template_name = "questionnaire/heating_controls.html"
    form_class = questionnaire_forms.HeatingControls
    next = "InConservationArea"

    def get_initial(self):
        data = super().get_initial()
        for field in self.get_form_class().declared_fields:
            orig_field = field + "_orig"
            data[field] = getattr(self.answers, field)
            if data[field] is None:
                data[field] = getattr(self.answers, orig_field, None)

        return data

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        for field in self.get_form_class().declared_fields:
            orig_field = field + "_orig"
            context[orig_field] = getattr(self.answers, orig_field, None)
            if context[orig_field]:
                context["any_orig"] = True

        return context


class StorageHeatersPresent(abstract_views.SinglePrePoppedQuestion):
    title = "Storage heaters"
    question = "Are there storage heaters in the property?"
    type_ = abstract_views.QuestionType.YesNo
    next = "HhrshsPresent"

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.storage_heaters_present:
            self.answers.electric_radiators_present = None
        else:
            self.answers.hhrshs_present = None

    def get_next(self):
        if self.answers.storage_heaters_present:
            return "HhrshsPresent"
        else:
            return "ElectricRadiatorsPresent"


class ElectricRadiatorsPresent(abstract_views.SinglePrePoppedQuestion):
    title = "Electric radiators"
    question = "Are there other electric radiators in the property?"
    note = "These may be fixed panel radiators or freestanding heaters."
    type_ = abstract_views.QuestionType.YesNo
    next = "InConservationArea"


class HhrshsPresent(abstract_views.SingleQuestion):
    title = "Storage heater performance"
    question = "Are the storage heaters in the property Diplex Quantum or other high heat retention storage heaters?"
    type_ = abstract_views.QuestionType.YesNo
    next = "InConservationArea"


class InConservationArea(abstract_views.SingleQuestion):
    title = "Conservation area"
    question = "Is this property in a conservation area?"
    type_ = abstract_views.QuestionType.YesNo

    def get_next(self):
        if selectors.data_was_changed(self.answers):
            return "AccuracyWarning"
        else:
            return "RecommendedMeasures"


class AccuracyWarning(abstract_views.Question):
    template_name = "questionnaire/accuracy_warning.html"
    title = "Data has been changed"
    next = "Occupants"


class Occupants(abstract_views.Question):
    template_name = "questionnaire/occupants.html"
    title = "Household composition"
    next = "HouseholdIncome"
    form_class = questionnaire_forms.Occupants


class HouseholdIncome(abstract_views.SingleQuestion):
    answer_field = "total_income_lt_30k"
    question = "Is the accumulated income of all the people living in the property less than £30,000 (before tax)?"
    title = "Gross household income"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.IncomeIsUnderThreshold.choices

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.total_income_lt_30k == enums.IncomeIsUnderThreshold.YES.value:
            self.answers.take_home_lt_30k = enums.IncomeIsUnderThreshold.YES.value
            self.answers.disability_benefits = None
            self.answers.child_benefit = None
            self.answers.child_benefit_threshold = None
            self.answers.income_lt_child_benefit_threshold = None

    def get_next(self):
        if self.answers.total_income_lt_30k == enums.IncomeIsUnderThreshold.YES.value:
            return "Vulnerabilities"
        else:
            return "HouseholdTakeHomeIncome"


class HouseholdTakeHomeIncome(abstract_views.SingleQuestion):
    answer_field = "take_home_lt_30k"
    question = (
        "Is the accumulated take home pay (after tax and deductions) of all people living "
        "in the property less than £30,000?"
    )
    note = "This is the household income after housing costs (mortgage or rent) and energy bills have been deducted."
    title = "Total household take-home pay"
    next = "DisabilityBenefits"
    type_ = abstract_views.QuestionType.Choices
    choices = enums.IncomeIsUnderThreshold.choices


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

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.disability_benefits:
            self.answers.child_benefit = None
            self.answers.child_benefit_threshold = None
            self.answers.income_lt_child_benefit_threshold = None

    def get_next(self):
        if self.answers.disability_benefits:
            return "Vulnerabilities"
        else:
            return "ChildBenefit"


class ChildBenefit(abstract_views.SingleQuestion):
    title = "Child benefit"
    next = "IncomeLtChildBenefitThreshold"
    type_ = abstract_views.QuestionType.YesNo
    question = "Does anybody living in the home receive Child Benefit?"

    def pre_save(self):
        # Set the benefit threshold dependent on the household composition
        if not self.answers.child_benefit:
            # Obliterate values from the etc.
            self.answers.child_benefit_threshold = None
            self.answers.income_lt_child_benefit_threshold = None


class IncomeLtChildBenefitThreshold(abstract_views.SingleQuestion):
    title = "Income in relation to child benefit threshold"
    next = "Vulnerabilities"
    type_ = abstract_views.QuestionType.YesNo

    def get_question(self):
        return f"Is the household income less than £{self.answers.child_benefit_threshold:,}?"

    def prereq(self):
        if self.answers.child_benefit:
            self.answers.child_benefit_threshold = utils.get_child_benefit_threshold(
                self.answers
            )
        else:
            # Shouldn't be in this branch. This should not ever happen.
            return self.redirect()


class Vulnerabilities(abstract_views.Question):
    template_name = "questionnaire/vulnerabilities.html"
    title = "Specific vulnerabilities of household members"
    next = "RecommendedMeasures"
    form_class = questionnaire_forms.Vulnerabilities


class RecommendedMeasures(abstract_views.Question):
    template_name = "questionnaire/recommended_measures.html"
    title = "Recommendations for this property"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        measures = utils.determine_recommended_measures(self.answers)
        for measure in measures:
            measure.disruption = utils.get_disruption(measure)
            measure.comfort_benefit = utils.get_comfort_benefit(measure)
            measure.bill_impact = utils.get_bill_impact(measure)
            measure.funding_likelihood = utils.get_funding_likelihood(measure)

        context["measures"] = measures
        context["sw_insulation_warning"] = (
            enums.PossibleMeasures.SOLID_WALL_INSULATION in context["measures"]
            and self.answers.in_conservation_area is True
        )

        context["rating"] = utils.get_overall_rating(self.answers)

        return context

    def get_next(self):
        if self.request.POST.get("finish_now", "") == "True":
            services.close_questionnaire(self.answers)
            return "Completed"
        else:
            return "ToleratedDisruption"


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
    title = "Your ability to contribute"
    question = "What condition is the property currently in?"
    type_ = abstract_views.QuestionType.Choices
    next = "Motivations"

    def get_choices(self):
        # Only non-owners get to answer "I don't know"
        if self.answers.is_owner:
            return enums.StateOfRepair.choices[:-1]
        else:
            return enums.StateOfRepair.choices


class Motivations(abstract_views.Question):
    title = "Motivations"
    template_name = "questionnaire/motivations.html"
    form_class = questionnaire_forms.Motivations
    next = "ContributionCapacity"

    def get_context_data(self):
        data = super().get_context_data()
        data["is_owner"] = self.answers.is_owner

        return data

    def pre_save(self):
        if self.answers.motivation_unknown:
            self.answers.motivation_better_comfort = None
            self.answers.motivation_lower_bills = None
            self.answers.motivation_environment = None


class ContributionCapacity(abstract_views.SingleQuestion):
    title = "Your ability to contribute"
    type_ = abstract_views.QuestionType.Choices

    def get_question(self):
        if self.answers.is_owner:
            return (
                "Would you be willing to contribute towards a package of improvements "
                "to your home in order to get the best outcome for your home?"
            )
        else:
            return (
                "Would the owner be willing to contribute towards a package of "
                "improvements in order to get the best outcome for their home?"
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
            if utils.calculate_household_income(self.answers) < 30000:
                self.answers.take_home_lt_30k_confirmation = True


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


class NothingAtThisTime(abstract_views.Question):
    template_name = "questionnaire/nothing_at_this_time.html"
    form_class = questionnaire_forms.NothingAtThisTime

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["future_schemes_consent_given"] = self.answers.consented_future_schemes
        context["rating"] = utils.get_overall_rating(self.answers)
        return context

    def get_next(self):
        services.close_questionnaire(self.answers)
        return "Completed"


class Completed(TemplateView):
    template_name = "questionnaire/completed.html"
