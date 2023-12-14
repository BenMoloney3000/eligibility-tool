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

from prospector.apps.questionnaire import forms as questionnaire_forms
from prospector.apps.questionnaire import models
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


class NoQuestion(Question):
    """Produces a non-question view, e.g. summary or info view."""

    type_: QuestionType
    question: None
    next: str


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
    icon: Optional[str]

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
        if hasattr(self, "icon"):
            context["question_icon"] = self.icon
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
            form_fields["data_correct"].label = "Is this correct?"

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
