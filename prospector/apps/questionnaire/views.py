import contextlib
import logging
from enum import auto
from enum import Enum
from typing import Optional

from django import forms
from django.utils import timezone
from django.views.generic.edit import FormView

from . import forms as questionnaire_forms
from . import models
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

    # Make the signup accessible to the form logic
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["answers"] = self.answers
        return kwargs

    def form_valid(self, form):
        """
        Save form fields to the Signup.

        Fields that match Signup fields will be saved, anything else discarded.
        """
        for k, v in form.cleaned_data.items():
            setattr(self.signup, k, v)

        # This gives questions an opportunity to do extra processing, lookups etc.
        # before we save, saving unnecessary round trips to the database.
        if hasattr(self, "pre_save"):
            self.pre_save()

        self.signup.save()

        return self.redirect(self.get_next())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

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
    and concise as possible.  It inherits from the Question class above and
    cannot run independently from it.
    """

    type_: QuestionType
    question: str
    supplementary: Optional[str]
    note: Optional[str]
    unit: Optional[str]
    next: Optional[str]

    template_name = "impact_tracker/question.html"

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
        #  difficult to maintain, and splits forms and views that are intimately related
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
    template_name = "questionnaire/respondent_name.html"
    next = "RespondentRole"
    form_class = questionnaire_forms.RespondentName
