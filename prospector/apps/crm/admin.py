from django.contrib import admin
from import_export.admin import ExportMixin

from . import models


@admin.register(models.CrmResult)
class QuestionnaireAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        "answers",
        "created_at",
        "state",
        "result",
    )
