from django.contrib import admin

from import_export.admin import ExportMixin

from . import models


@admin.register(models.Answers)
class QuestionnaireAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "property_postcode",
        "updated_at",
        "completed_at",
    )
