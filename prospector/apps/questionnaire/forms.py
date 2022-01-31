from django import forms
from django.utils.safestring import mark_safe

from . import enums
from . import models


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
        self.error_class = StyledErrorList


class RespondentName(AnswerFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    class Meta:
        model = models.Answers
        fields = [
            "first_name",
            "last_name",
        ]


class RespondentRelationship(AnswerFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["respondent_relationship"].required = True
        self.fields["respondent_has_permission"].required = True

    class Meta:
        model = models.Answers
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
