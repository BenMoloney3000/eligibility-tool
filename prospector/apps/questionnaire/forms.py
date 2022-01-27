from django import forms
from django.utils.safestring import mark_safe

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
    class Meta:
        model = models.Answers
        fields = [
            "first_name",
            "last_name",
        ]
