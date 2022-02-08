import contextlib
import dataclasses
import logging
from enum import auto
from enum import Enum
from typing import Optional

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.views.generic.edit import FormView

from . import enums
from . import forms as questionnaire_forms
from . import models
from . import services
from prospector.apis import epc
from prospector.apis import ideal_postcodes
from prospector.dataformats import postcodes
from prospector.trail import mixin


logger = logging.getLogger(__name__)


SESSION_ANSWERS_ID = "questionnaire:answer_id"
SESSION_TRAIL_ID = "questionnaire:trail_id"
SESSION_POSTCODE_CACHE = "cached_postcodes"


class QuestionType(Enum):
    Int = auto()
    Text = auto()
    YesNo = auto()
    Decimal = auto()
    Choices = auto()
    MultipleChoices = auto()


class PostcodeCacherMixin:
    def get_postcode(self, postcode):
        """Check session-cached postcodes before hitting the API.

        Uses normalised postcodes. Possible TODO: put this into the DB with a TTL.
        """
        if SESSION_POSTCODE_CACHE not in self.request.session:
            self.request.session[SESSION_POSTCODE_CACHE] = {}

        if postcode in self.request.session[SESSION_POSTCODE_CACHE]:
            return ideal_postcodes._process_results(
                self.request.session[SESSION_POSTCODE_CACHE][postcode]
            )
        else:
            addresses = ideal_postcodes.get_for_postcode(postcode)
            self.request.session[SESSION_POSTCODE_CACHE][postcode] = [
                dataclasses.asdict(address) for address in addresses
            ]
            # session change detector won't look into our dict so needs nudge
            self.request.session.modified = True
            return addresses


class Question(mixin.TrailMixin, FormView):
    """The custom trail class for the whole survey."""

    trail_initial = ["Start"]

    trail_session_id = SESSION_TRAIL_ID
    trail_url_prefix = "questionnaire:"
    form_class = questionnaire_forms.DummyForm

    def _init_answers(self):
        # Don't let us get called more than once.
        if hasattr(self, "answers"):
            return

        self.answers = None
        if SESSION_ANSWERS_ID in self.request.session:
            with contextlib.suppress(models.Answers.DoesNotExist):
                self.answers = models.Answers.objects.filter(
                    id=self.request.session[SESSION_ANSWERS_ID]
                ).first()

        if not self.answers:
            self.answers = models.Answers.objects.create()
            self.request.session[SESSION_ANSWERS_ID] = self.answers.id

            # if we had a trail, wipe it, forcing us back to the start.
            if SESSION_TRAIL_ID in self.request.session:
                del self.request.session[SESSION_TRAIL_ID]

    def dispatch(self, request, *args, **kwargs):
        self._init_answers()
        return super().dispatch(request, *args, **kwargs)

    # Make the answers accessible to the form logic
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["answers"] = self.answers
        return kwargs

    def get_initial(self):
        # Populate form fields from model first.
        # This will need to be overridden if non-model form fields are present
        data = {}

        # Do we have any model form fields in the form?
        form_class = self.get_form_class()
        if hasattr(form_class, "_meta"):
            for field in self.get_form_class()._meta.fields:
                if hasattr(self.answers, field):
                    data[field] = getattr(self.answers, field)

        return data

    def form_valid(self, form):
        """
        Save form fields to the answers.

        Fields that match Answers fields will be saved, anything else discarded.
        """
        for k, v in form.cleaned_data.items():
            setattr(self.answers, k, v)

        # This gives questions an opportunity to do extra processing, lookups etc.
        # before we save, saving unnecessary round trips to the database.
        if hasattr(self, "pre_save"):
            self.pre_save()

        self.answers.save()

        return self.redirect(self.get_next())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["prev_url"] = self.get_prev_url()
        context["title"] = self.get_title()

        return context

    def get_title(self):
        """Get a page title for the HTML <title> tag."""

        if hasattr(self, "title"):
            return self.title

        return self.__class__.__name__


class SingleQuestion(Question, mixin.TrailMixin):
    """
    Produces a 'standard' single question view.

    This uses a load of metaprogramming to make the question definitions as simple
    and concise as possible, meaning that a separate form class definition is
    not required this view. It inherits from the Question class above.
    """

    type_: QuestionType
    question: str
    supplementary: Optional[str]
    note: Optional[str]
    unit: Optional[str]
    next: Optional[str]

    template_name = "questionnaire/single_question.html"

    def _type_to_field(self):
        if self.type_ is QuestionType.Int:
            return forms.IntegerField(required=True)
        elif self.type_ is QuestionType.Text:
            return forms.CharField(required=True)
        elif self.type_ is QuestionType.YesNo:
            # https://code.djangoproject.com/ticket/2723#comment:18
            return forms.TypedChoiceField(
                coerce=lambda x: x == "True",
                choices=self.get_choices(),
                widget=forms.RadioSelect,
                required=True,
            )
        elif self.type_ is QuestionType.Decimal:
            return forms.DecimalField(required=True)
        elif self.type_ is QuestionType.Choices:
            return forms.ChoiceField(
                widget=forms.RadioSelect, required=True, choices=self.get_choices()
            )
        elif self.type_ is QuestionType.MultipleChoices:
            return forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                required=False,
                choices=self.get_choices(),
            )
        else:
            raise NotImplementedError(f"{self.type_} not implemented")

    def get_form_class(self):
        this = self

        def clean_field(self):
            data = self.cleaned_data["field"]
            if hasattr(this, "validate_answer"):
                this.validate_answer(data)
            return data

        # Instead of defining a separate form for each page, which is repetitious,
        # difficult to maintain, and splits forms and views that are intimately related
        # across files, we instead specify a limited number of question types.
        #
        # Each question view has one type, and we generate the form dynamically here.
        QuestionForm = type(
            "QuestionForm",
            (questionnaire_forms.AnswerFormMixin, forms.Form),
            {"field": self._type_to_field(), "clean_field": clean_field},
        )

        return QuestionForm

    def get_choices(self):
        # This is overridable for when we want to provide dynamic choices.
        if self.type_ is QuestionType.YesNo and not hasattr(self, "choices"):
            # Default for Yes/No field
            return ((True, "Yes"), (False, "No"))
        return self.choices

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["question_text"] = self.get_question()

        context["question_supplement"] = self.get_supplementary()
        if hasattr(self, "unit"):
            context["unit"] = self.unit
        context["question_note"] = self.get_note()
        return context

    def get_answer_field(self):
        """
        Return the name of the field that contains the answer to this question.

        Normally we generate this automatically from the class name - so a class
        LivesInGermany will look for the answer in lives_in_germany.  However, there
        are times when you want to override this - you can do this by specifying
        answer_field on the class, or by overriding this function if you need more
        dynamic behaviour.
        """
        if hasattr(self, "answer_field"):
            return self.answer_field
        else:
            return mixin.snake_case(self.__class__.__name__, separator="_")

    def get_initial(self, *args, **kwargs):
        return {"field": getattr(self.answers, self.get_answer_field())}

    def sanitise_answer(self, data):
        """
        Sanitise the data received in some way.

        Override this when you need to normalise incoming data in some way.
        """
        return data

    def get_question(self):
        """Override this to set the question text dynamically."""
        if hasattr(self, "question"):
            return self.question

    def get_supplementary(self):
        """Override this to set the supplementary text dynamically."""
        if hasattr(self, "supplementary"):
            return self.supplementary

    def get_note(self):
        """Override this to set notes dynamically."""
        if hasattr(self, "note"):
            return self.note

    def form_valid(self, form):
        sanitised = self.sanitise_answer(form.cleaned_data["field"])
        field_name = self.get_answer_field()
        setattr(self.answers, field_name, sanitised)

        # This gives questions an opportunity to do extra processing, lookups etc.
        # before we save, saving unnecessary round trips to the database.
        if hasattr(self, "pre_save"):
            self.pre_save()

        self.answers.save()

        return self.redirect(self.get_next())


class SinglePrePoppedQuestion(SingleQuestion):
    """
    Produce a 'standard' single question view with prepopulated property data.

    Mirrors the PrePoppedMixin for forms. Adds in a 'data_correct' boolean field
    and uses the data field value as the initial field value (if no value for the
    field already) as well as putting it into context.
    """

    template_name = "questionnaire/single_prepopped_question.html"

    def get_form_class(self):
        this = self

        def clean_field(self):
            data = self.cleaned_data["field"]
            if hasattr(this, "validate_answer"):
                this.validate_answer(data)
            return data

        # TODO: catch where the field is a YesNo, in which case the 'data_correct'
        # field will tell us the correct answer!

        # "Data is correct" field is required if we have a data-derived answer
        prepopped_data_is_present = (
            self.get_prepop_data() is not None and self.get_prepop_data() != ""
        )
        QuestionForm = type(
            "QuestionForm",
            (questionnaire_forms.AnswerFormMixin, forms.Form),
            {
                "field": self._type_to_field(),
                "data_correct": forms.TypedChoiceField(
                    coerce=lambda x: x == "True",
                    choices=(
                        (True, "This is correct"),
                        (False, "I want to correct this"),
                    ),
                    widget=forms.RadioSelect,
                    required=prepopped_data_is_present,
                ),
                "clean_field": clean_field,
            },
        )

        return QuestionForm

    def get_prepop_field(self):
        return self.get_answer_field() + "_orig"

    def get_prepop_data(self):
        # Return any data-derived prediction for this field.
        return getattr(self.answers, self.get_prepop_field())

    def get_initial(self):
        # Populate form fields from model, using the _orig field as an initial initial
        data = {}

        if getattr(self.answers, self.get_answer_field()):
            data["field"] = getattr(self.answers, self.get_answer_field())
            data["data_correct"] = data["field"] == self.get_prepop_data()
        else:
            data["field"] = self.get_prepop_data()

        return data

    def get_context_data(self, *args, **kwargs):
        # Get the default value and un-Enum if it necessary.
        context = super().get_context_data(*args, **kwargs)
        context["data_orig"] = self.get_prepop_data()

        # Check for enum or other model property formatter
        data_orig_display = "get_" + self.get_prepop_field() + "_display"
        if context["data_orig"] and hasattr(self.answers, data_orig_display):
            context["data_orig"] = getattr(self.answers, data_orig_display)()
        if self.type_ == QuestionType.YesNo:
            context["data_orig"] = "Yes" if context["data_orig"] else "No"

        return context

    def form_valid(self, form):
        # If they answer "Yes it's correct" ignore anything set underneath
        if form.cleaned_data["data_correct"] and self.get_prepop_data():
            setattr(self.answers, self.get_answer_field(), self.get_prepop_data())
        else:
            sanitised = self.sanitise_answer(form.cleaned_data["field"])
            field_name = self.get_answer_field()
            setattr(self.answers, field_name, sanitised)

        # This gives questions an opportunity to do extra processing, lookups etc.
        # before we save, saving unnecessary round trips to the database.
        if hasattr(self, "pre_save"):
            self.pre_save()

        self.answers.save()

        return self.redirect(self.get_next())


class Start(SingleQuestion):
    template_name = "questionnaire/start.html"
    type_ = QuestionType.YesNo
    title = "About this tool"
    answer_field = "terms_accepted_at"
    question = "Please confirm that you have read and accept our data privacy policy."
    next = "RespondentName"

    def pre_save(self):
        self.answers.terms_accepted_at = timezone.now()


class RespondentName(Question):
    title = "Your name"
    template_name = "questionnaire/respondent_name.html"
    next = "RespondentRole"
    form_class = questionnaire_forms.RespondentName


class RespondentRole(SingleQuestion):
    title = "Your role"
    type_ = QuestionType.Choices
    question = "Are you the occupant of the property for which you're enquiring?"
    answer_field = "is_occupant"
    choices = (
        (True, "Yes, I am the homeowner or tenant of this property."),
        (False, "No, I am acting on behalf of the tenant or homeowner."),
    )

    def pre_save(self):
        self.answers.is_occupant = self.answers.is_occupant == "True"

        if self.answers.is_occupant:
            # For safety, erase all the details describing a non-occupant respondent
            self.answers.address_1 = ""
            self.answers.address_2 = ""
            self.answers.address_3 = ""
            self.answers.udprn = None
            self.answers.postcode = ""
            self.answers.respondent_has_permission = None
            self.answers.respondent_relationship = ""
            self.answers.respondent_relationship_other = ""

    def get_next(self):
        if self.answers.is_occupant:
            return "Email"
        else:
            return "RespondentRelationship"


class RespondentRelationship(Question):
    title = "Your relationship to the occupant"
    question = "What is your relationship to the occupant of the property for which you're enquiring?"
    form_class = questionnaire_forms.RespondentRelationship
    template_name = "questionnaire/respondent_relationship.html"

    def get_initial(self):
        data = super().get_initial()

        # Specific case here - initial data from DB can only be true or null, otherwise
        # the whole Answers object gets deleted.
        if data.get("respondent_has_permission"):
            data["respondent_has_permission"] = "True"

        return data

    def pre_save(self):
        if self.answers.respondent_relationship != enums.RespondentRelationship.OTHER:
            self.answers.respondent_relationship_other = ""
        self.answers.respondent_has_permission = (
            self.answers.respondent_has_permission == "True"
        )

    def get_next(self):
        if not self.answers.respondent_has_permission:
            return "NeedPermission"
        else:
            return "Postcode"


class NeedPermission(Question):
    title = "Sorry, we can't help you."
    template_name = "questionnaire/need_permission.html"

    def get_initial(self):
        # If we don't have permission, we need to delete everything entered so far
        self.answers.delete()


class Postcode(SingleQuestion):
    title = "Your postcode"
    type_ = QuestionType.Text
    question = "Enter your postcode"
    supplementary = (
        "This is the postcode for your own address, which may be different from the property "
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


class RespondentAddress(Question, PostcodeCacherMixin):
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
                for address in self.get_postcode(self.answers.postcode)
            }
        except ValueError:
            pass

        kwargs["prefilled_addresses"] = self.prefilled_addresses
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["postcode"] = self.answers.postcode
        context["all_postcode_addresses"] = self.prefilled_addresses
        return context

    def pre_save(self):
        if self.answers.udprn and int(self.answers.udprn) in self.prefilled_addresses:
            selected_address = self.prefilled_addresses[int(self.answers.udprn)]
            if not self.answers.address_1:
                # Populate fields if it wasn't already done by JS
                self.answers.address_1 = selected_address.line_1
                self.answers.address_2 = selected_address.line_2
                self.answers.address_3 = selected_address.line_3
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


class Email(SingleQuestion):
    title = "Your email address"
    type_ = QuestionType.Text
    question = "Enter your email address"
    next = "ContactPhone"

    @staticmethod
    def validate_answer(field):
        validate_email(field)


class ContactPhone(Question):
    title = "Your phone number"
    form_class = questionnaire_forms.RespondentPhone
    template_name = "questionnaire/respondent_phone.html"

    def get_next(self):
        if self.answers.is_occupant:
            return "PropertyAddress"
        else:
            return "OccupantName"


class OccupantName(Question):
    title = "Occupant name"
    template_name = "questionnaire/occupant_name.html"
    form_class = questionnaire_forms.OccupantName
    next = "PropertyPostcode"


class PropertyPostcode(SingleQuestion):
    title = "Property postcode"
    type_ = QuestionType.Text
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


class PropertyAddress(Question, PostcodeCacherMixin):
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


class PropertyOwnership(SingleQuestion):
    title = "Property ownership"
    type_ = QuestionType.Choices
    question = "What is the tenure of the property - how is it occupied?"
    choices = enums.PropertyOwnership.choices
    next = "Consents"


class Consents(Question):
    title = "Your consent to our use of your data"
    question = "Please confirm how we can use your data"
    template_name = "questionnaire/consents.html"
    form_class = questionnaire_forms.Consents
    next = "SelectEPC"

    def get_initial(self):
        data = super().get_initial()

        granted = models.ConsentGranted.objects.filter(granted_for=self.answers)
        for grant in granted:
            consent = enums.Consent(grant.consent)
            data[consent.name.lower()] = True

        return data

    def pre_save(self):
        # Sync the consents, which will have been temporarily saved onto the answers object

        # Could save a few DB calls by compiling the consents into a list
        for consent, data in self.get_form().fields.items():
            if getattr(self.answers, consent, False):
                models.ConsentGranted.objects.update_or_create(
                    granted_for=self.answers,
                    consent=enums.Consent[consent.upper()],
                    defaults={"granted_at": timezone.now()},
                )
            else:
                models.ConsentGranted.objects.filter(
                    granted_for=self.answers,
                    consent=enums.Consent[consent.upper()],
                ).delete()


class SelectEPC(Question):
    title = "Your EPC"
    template_name = "questionnaire/select_epc.html"
    form_class = questionnaire_forms.SelectEPC
    next = "PropertyType"
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


class PropertyType(Question):
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


class PropertyAgeBand(SinglePrePoppedQuestion):
    title = "Property age"
    question = "When was the property built?"
    type_ = QuestionType.Choices
    choices = enums.PropertyAgeBand.choices
    next = "WallType"

    def pre_save(self):
        # If we didn't get the likely wall type, infer from the age now.
        if not self.answers.wall_type_orig:
            self.answers.wall_type_orig = int(self.answers.property_age_band) < 1930


class WallType(SinglePrePoppedQuestion):
    title = "Wall type"
    question = "What type of outside walls does your property have?"
    type_ = QuestionType.Choices
    choices = enums.WallType.choices
    note = (
        "If the property has more than one type of outside wall, choose the one "
        "that makes up the most of the external area."
    )
    next = "WallsInsulated"


class WallsInsulated(SinglePrePoppedQuestion):
    title = "Wall type"
    question = "Are the outside walls in your house insulated?"
    type_ = QuestionType.YesNo
    note = (
        "If only some of the outside walls are insulated, choose the option that "
        "applies to the largest external area."
    )
    next = "SuspendedFloor"


class SuspendedFloor(SinglePrePoppedQuestion):
    title = "Floor type"
    question = "Does the property have a suspended timber floor with a void underneath?"
    type_ = QuestionType.YesNo
    note = (
        "If your property has different types of floor, choose the option that applies "
        "to the largest floor area. If you live in a non-ground-floor flat, select 'No'."
    )
    next = "UnheatedLoft"


class UnheatedLoft(SinglePrePoppedQuestion):
    title = "Property roof"
    question = "Does the property have an unheated loft space directly above it?"
    type_ = QuestionType.YesNo
    note = "If you live in a non-top-floor flat, the answer is 'No'."
    next = "UnheatedLoftSpace"

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.unheated_loft:
            self.answers.room_in_roof = None
            self.answers.rir_insulated = None
            self.answers.flat_roof = None
            self.answers.flat_roof_modern = None
        else:
            self.answers.roof_space_insulated = None

    def get_next(self):
        if self.answers.unheated_loft:
            return "RoofSpaceInsulated"
        else:
            return "RoomInRoof"


class RoomInRoof(SinglePrePoppedQuestion):
    title = "Room in roof"
    question = "Is there a room in the roof space of the property, as a loft conversion or otherwise?"
    type_ = QuestionType.YesNo
    next = "RirInsulated"

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.room_in_roof:
            self.answers.flat_roof = None
            self.answers.flat_roof_modern = None
        else:
            self.answers.rir_insulated = None

    def get_next(self):
        if self.answers.room_in_roof:
            return "RirInsulated"
        else:
            return "FlatRoof"


class RirInsulated(SinglePrePoppedQuestion):
    title = "Room in roof insulation"
    question = "Has the room in the roof space been well insulated?"
    type_ = QuestionType.YesNo
    next = "GasBoilerPresent"


class RoofSpaceInsulated(SinglePrePoppedQuestion):
    title = "Loft insulation"
    question = "Has the unheated loft space been well insulated?"
    type_ = QuestionType.YesNo
    next = "GasBoilerPresent"
    note = "By 'well insulated' we mean with at least 250mm of mineral wool, or equivalent."


class FlatRoof(SinglePrePoppedQuestion):
    title = "Flat roof"
    question = "Does the property have a flat roof?"
    type_ = QuestionType.YesNo
    note = (
        "If the property has different roof types, choose the answer that applies "
        "to the largest roof area."
    )

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if not self.answers.flat_roof:
            self.answers.flat_roof_modern = None

    def get_next(self):
        if self.answers.flat_roof:
            return "FlatRoofModern"
        else:
            return "GasBoilerPresent"


class FlatRoofModern(SingleQuestion):
    title = "Flat roof type"
    question = "Was the flat roof built or insulated since 1980?"
    type_ = QuestionType.YesNo
    next = "GasBoilerPresent"


class GasBoilerPresent(SinglePrePoppedQuestion):
    title = "Gas boiler"
    question = (
        "Does the property have a heating system with a boiler running off mains gas?"
    )
    type_ = QuestionType.YesNo

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if self.answers.gas_boiler_present:
            self.answers.other_heating_present = None
            self.answers.other_heating_fuel = ""
            self.answers.storage_heaters_present = None
            self.answers.hhrshs_present = None
        else:
            self.answers.gas_boiler_age = ""
            self.answers.gas_boiler_broken = None

    def get_next(self):
        if self.answers.gas_boiler_present:
            return "HwtPresent"
        else:
            return "OtherHeatingPresent"


class OtherHeatingPresent(SinglePrePoppedQuestion):
    title = "Other central heating system"
    question = "Does the property have a non-gas central heating system?"
    type_ = QuestionType.YesNo

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


class HwtPresent(SingleQuestion):
    title = "Hot water tank"
    question = "Does the property have a hot water tank?"
    type_ = QuestionType.YesNo

    def get_next(self):
        if self.answers.gas_boiler_present:
            return "GasBoilerAge"
        else:
            return "OtherHeatingFuel"


class OtherHeatingFuel(SinglePrePoppedQuestion):
    title = "Heating fuel source"
    question = "What fuel does your central heating system run on?"
    type_ = QuestionType.Choices
    choices = enums.NonGasFuel.choices
    next = "ConservationArea"


class GasBoilerAge(SingleQuestion):
    title = "Boiler age"
    question = "When was the current boiler installed?"
    type_ = QuestionType.Choices
    choices = enums.BoilerAgeBand.choices
    next = "GasBoilerBroken"


class GasBoilerBroken(SingleQuestion):
    title = "Boiler condition"
    question = "Is the gas boiler currently broken?"
    type_ = QuestionType.YesNo
    next = "HeatingControls"


class HeatingControls(Question):
    title = "Heating controls"
    template_name = "questionnaire/heating_controls.html"
    form_class = questionnaire_forms.HeatingControls
    next = "ConservationArea"

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


class StorageHeatersPresent(SinglePrePoppedQuestion):
    title = "Storage heaters"
    question = "Are there storage heaters in the property?"
    type_ = QuestionType.YesNo
    next = "HhrshsPresent"

    def pre_save(self):
        # Obliterate values from the path never taken (in case of reversing)
        if not self.answers.storage_heaters_present:
            self.answers.hhrshs_present = None

    def get_next(self):
        if self.answers.storage_heaters_present:
            return "HhrshsPresent"
        else:
            return "ConservationArea"


class HhrshsPresent(SingleQuestion):
    title = "Storage heater performance"
    question = "Are the storage heaters in the property Diplex Quantum or other high heat retention storage heaters?"
    type_ = QuestionType.YesNo
    next = "ConservationArea"


class ConservationArea(SingleQuestion):
    title = "Conservation area"
    question = "Is this property in a conservation area?"
    type_ = QuestionType.YesNo
    next = "AccuracyWarning"
