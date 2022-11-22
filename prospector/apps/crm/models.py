from django.db import models

from prospector.apps.questionnaire.models import Answers


class CrmState(models.TextChoices):
    SUCCESS = "SUCCESS", "Status Success"
    FAILURE = "FAILURE", "Status Failure"


class CrmResult(models.Model):
    answers = models.ForeignKey(Answers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        max_length=32, choices=CrmState.choices, db_index=True, blank=True
    )
    result = models.JSONField(null=True)
