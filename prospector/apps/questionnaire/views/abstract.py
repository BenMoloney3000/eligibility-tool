import contextlib
import logging
from enum import auto
from enum import Enum
from typing import Optional

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Field
from crispy_forms_gds.layout import Layout
from crispy_forms_gds.layout import Size
from django import forms
from django.views.generic.edit import FormView

from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import forms as questionnaire_forms
from prospector.apps.questionnaire import models
from prospector.apps.questionnaire import services
from prospector.apps.questionnaire import utils
from prospector.trail import mixin


logger = logging.getLogger(__name__)


SESSION_ANSWERS_ID = "questionnaire:answer_id"
SESSION_TRAIL_ID = "questionnaire:trail_id"


class QuestionType(Enum):
    Int = auto()
    Text = auto()
    YesNo = auto()
    Decimal = auto()
    Choices = auto()
    MultipleChoices = auto()


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
                    id=self.request.session[SESSION_ANSWERS_ID],
                    completed_at__isnull=True,
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
        context["percent_complete"] = self.get_percent_complete()

        return context

    def get_title(self):
        """Get a page title for the HTML <title> tag."""

        if hasattr(self, "title"):
            return self.title

        return self.__class__.__name__

    def get_percent_complete(self) -> int:
        return getattr(self, "percent_complete", 0)


class SingleQuestion(Question):
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
    A 'standard' single question view with a value presented from third party property data.

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

        def init(cls, *args, **kwargs):
            super(type(cls), cls).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(
                Field.radios(
                    "field", legend_size=Size.MEDIUM, legend_tag="h1", inline=True
                ),
            )

        form_fields = {
            "field": self._type_to_field(),
            "clean_field": clean_field,
            "__init__": init,
        }

        # Add 'Data is correct' field if this isn't a boolean field
        # and we have a data-derived answer.
        prepopped_data_is_present = (
            self.get_prepop_data() is not None and self.get_prepop_data() != ""
        )
        if prepopped_data_is_present and self.type_ != QuestionType.YesNo:
            form_fields["data_correct"] = forms.TypedChoiceField(
                coerce=lambda x: x == "True",
                choices=(
                    (True, "This is correct"),
                    (False, "I want to correct this"),
                ),
                widget=forms.RadioSelect,
                required=True,
            )
            form_fields["data_correct"].label = False

        QuestionForm = type(
            "QuestionForm",
            (questionnaire_forms.AnswerFormMixin, forms.Form),
            form_fields,
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

        if getattr(self.answers, self.get_answer_field()) not in ["", None]:
            data["field"] = getattr(self.answers, self.get_answer_field())
            data["data_correct"] = data["field"] == self.get_prepop_data()
        else:
            data["field"] = self.get_prepop_data()

        return data

    def get_context_data(self, *args, **kwargs):
        # Get the default value and un-Enum if it necessary.
        context = super().get_context_data(*args, **kwargs)
        context["data_orig"] = self.get_prepop_data()

        # Check for enum (or other model property formatter)
        data_orig_display = "get_" + self.get_prepop_field() + "_display"
        if context["data_orig"] and hasattr(self.answers, data_orig_display):
            context["data_orig"] = getattr(self.answers, data_orig_display)()

        # Humanise booleans
        if self.type_ == QuestionType.YesNo and context["data_orig"] not in ["", None]:
            context["data_orig"] = "Yes" if context["data_orig"] else "No"

        context["question_type"] = self.type_

        return context

    def form_valid(self, form):
        # If they answer "Yes it's correct" ignore anything set underneath
        if form.cleaned_data.get("data_correct") and self.get_prepop_data():
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


class HouseholdAdultQuestion(Question):
    def _init_answers(self):
        """Initialise both Answers and HouseholdAdult models."""

        super()._init_answers()
        if hasattr(self, "household_adult"):
            return

        self.household_adult = models.HouseholdAdult.objects.get(
            adult_number=self.adult_number, answers=self.answers
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["full_name"] = self.household_adult.full_name
        context["adult_number"] = self.household_adult.adult_number

        return context

    def get_initial(self):
        # Populate form fields from model first.
        # This will need to be overridden if non-model form fields are present
        data = {}

        # Do we have any model form fields in the form?
        form_class = self.get_form_class()
        if hasattr(form_class, "_meta"):
            for field in self.get_form_class()._meta.fields:
                if hasattr(self.household_adult, field):
                    data[field] = getattr(self.household_adult, field)
        return data

    def form_valid(self, form):
        """
        Save form fields to the answers.

        Fields that match Answers fields will be saved, anything else discarded.
        """
        for k, v in form.cleaned_data.items():
            setattr(self.household_adult, k, v)

        # This gives questions an opportunity to do extra processing, lookups etc.
        # before we save, saving unnecessary round trips to the database.
        if hasattr(self, "pre_save"):
            self.pre_save()

        self.household_adult.save()

        return self.redirect(self.get_next())


class HouseholdAdultName(HouseholdAdultQuestion):
    form_class = questionnaire_forms.HouseholdAdultName
    template_name = "questionnaire/household_adults/name.html"

    def get_next(self):
        rating = utils.get_overall_rating(self.answers)
        if rating == enums.RAYG.YELLOW:
            return f"Adult{self.adult_number}WelfareBenefits"
        else:
            return f"Adult{self.adult_number}Employment"


class HouseholdAdultEmployment(HouseholdAdultQuestion):
    form_class = questionnaire_forms.HouseholdAdultEmployment
    template_name = "questionnaire/household_adults/employment.html"

    def get_next(self):
        employment = getattr(self.household_adult, "employment_status")
        if (
            employment == enums.EmploymentStatus.EMPLOYED.value
            or employment == enums.EmploymentStatus.OTHER.value
        ):
            self.household_adult.self_employment_income = 0
            self.household_adult.self_employment_income_frequency = ""
            self.household_adult.business_income = 0
            self.household_adult.business_income_frequency = ""
            self.household_adult.save()
            return f"Adult{self.adult_number}EmploymentIncome"
        elif employment == enums.EmploymentStatus.SELF_EMPLOYED.value:
            self.household_adult.employment_income = 0
            self.household_adult.employment_income_frequency = ""
            self.household_adult.save()
            return f"Adult{self.adult_number}SelfEmploymentIncome"
        else:
            self.household_adult.self_employment_income = 0
            self.household_adult.self_employment_income_frequency = ""
            self.household_adult.employment_income = 0
            self.household_adult.employment_income_frequency = ""
            self.household_adult.business_income = 0
            self.household_adult.business_income_frequency = ""
            self.household_adult.save()
            return f"Adult{self.adult_number}WelfareBenefits"


class HouseholdAdultEmploymentIncome(HouseholdAdultQuestion):
    form_class = questionnaire_forms.HouseholdAdultEmploymentIncome
    template_name = "questionnaire/household_adults/employment_income.html"

    def get_next(self):
        return f"Adult{self.adult_number}WelfareBenefits"


class HouseholdAdultSelfEmploymentIncome(HouseholdAdultQuestion):
    form_class = questionnaire_forms.HouseholdAdultSelfEmploymentIncome
    template_name = "questionnaire/household_adults/self_employment_income.html"

    def get_next(self):
        return f"Adult{self.adult_number}WelfareBenefits"


class HouseholdAdultWelfareBenefits(HouseholdAdultQuestion):
    form_class = questionnaire_forms.HouseholdAdultWelfareBenefits
    template_name = "questionnaire/household_adults/welfare_benefits.html"

    # Push the adult data into the form so it can set the benefit inputs dynamically
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["household_adult"] = self.household_adult
        return kwargs

    def get_next(self):
        any_benefits = services.sync_benefits(self.household_adult)

        if any_benefits:
            return f"Adult{self.adult_number}WelfareBenefitAmounts"
        else:
            return f"Adult{self.adult_number}PensionIncome"


class HouseholdAdultWelfareBenefitAmounts(HouseholdAdultQuestion):
    form_class = questionnaire_forms.HouseholdAdultWelfareBenefitAmounts
    template_name = "questionnaire/household_adults/welfare_benefit_amounts.html"

    # Push the adult data into the form so it can set the benefit inputs dynamically
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["household_adult"] = self.household_adult
        return kwargs

    def pre_save(self):
        services.save_benefit_amounts(self.household_adult)
        rating = utils.get_overall_rating(self.answers)

        # Delete data on path not taken
        if rating == enums.RAYG.YELLOW:
            self.household_adult.private_pension_income = 0
            self.household_adult.private_pension_income_frequency = ""
            self.household_adult.state_pension_income = 0
            self.household_adult.state_pension_income_frequency = ""

    def get_next(self):
        rating = utils.get_overall_rating(self.answers)
        if rating == enums.RAYG.YELLOW:
            total_adults = self.household_adult.answers.householdadult_set.count()
            if self.adult_number == total_adults:
                return "NothingAtThisTime"
            else:
                next_adult = self.adult_number + 1
                return f"Adult{next_adult}Name"
        else:
            return f"Adult{self.adult_number}PensionIncome"


class HouseholdAdultPensionIncome(HouseholdAdultQuestion):
    form_class = questionnaire_forms.HouseholdAdultPensionIncome
    template_name = "questionnaire/household_adults/pension_income.html"

    def pre_save(self):
        # If zero, lose the frequency
        if int(self.household_adult.private_pension_income) == 0:
            self.household_adult.private_pension_income_frequency = ""
        if int(self.household_adult.state_pension_income) == 0:
            self.household_adult.state_pension_income_frequency = ""

    def get_next(self):
        return f"Adult{self.adult_number}SavingsIncome"


class HouseholdAdultSavingsIncome(HouseholdAdultQuestion):
    form_class = questionnaire_forms.HouseholdAdultSavingsIncome
    template_name = "questionnaire/household_adults/savings_income.html"

    def pre_save(self):
        # If zero, lose the frequency
        if int(self.household_adult.saving_investment_income) == 0:
            self.household_adult.saving_investment_income_frequency = ""

    def get_next(self):
        total_adults = self.household_adult.answers.householdadult_set.count()
        if self.adult_number == total_adults:
            return "HouseholdSummary"
        else:
            next_adult = self.adult_number + 1
            return f"Adult{next_adult}Name"
