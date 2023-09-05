from django.contrib import admin

from . import models


@admin.register(models.ParityData)
class ParityDataAdmin(admin.ModelAdmin):
    list_display = ("org_ref",)
    readonly_fields = [field.name for field in models.ParityData._meta.get_fields()]
