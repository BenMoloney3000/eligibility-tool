from django.contrib import admin

from . import models


@admin.register(models.Answers)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "postcode",
        "updated_at",
        "completed_at",
    )
