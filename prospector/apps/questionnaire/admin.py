from django.contrib import admin
from django.contrib import messages
from django.db.models import BooleanField
from django.db.models import Case
from django.db.models import Count
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.translation import ngettext
from import_export.admin import ExportMixin

from . import models
from prospector.apps.crm.models import CrmResult
from prospector.apps.crm.tasks import crm_create


class CrmResultInline(admin.TabularInline):
    model = CrmResult


class CrmResultFilter(admin.SimpleListFilter):
    title = "Submitted"
    parameter_name = "crmresult_count"

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset

        crmresult_qs = queryset.annotate(
            crmresult_count=Count("crmresult"),
            has_crmresult=Case(
                When(Q(crmresult_count__gt=0), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )
        if value == "submitted":
            return crmresult_qs.filter(has_crmresult=True)
        elif value == "not_submitted":
            return crmresult_qs.filter(has_crmresult=False)

    def lookups(self, request, model_admin):
        return (
            ("submitted", "Submited to CRM"),
            ("not_submitted", "Not submited to CRM"),
        )


@admin.register(models.Answers)
class QuestionnaireAdmin(ExportMixin, admin.ModelAdmin):
    inlines = (CrmResultInline,)
    actions = ("crm_create",)
    list_display = (
        "id",
        "full_name",
        "property_postcode",
        "updated_at",
        "completed_at",
        "crmresults",
    )
    list_filter = (CrmResultFilter,)

    def get_queryset(self, request):
        return (
            super(QuestionnaireAdmin, self)
            .get_queryset(request)
            .annotate(crmresult_count=Count("crmresult"))
        )

    def crmresult_count(self, obj):
        return obj.crmresult_count

    crmresult_count.short_description = "CrmResult(s)"

    def crmresults(self, instance):
        info = (CrmResult._meta.app_label, CrmResult._meta.model_name)
        url = reverse(
            "admin:{}_{}_changelist".format(*info),
        )
        qs = {"answers_id__exact": instance.pk}
        return format_html(
            '<a href="{url}?{qs}">{text}</a>'.format(
                url=url, qs=urlencode(qs), text=instance.crmresult_count
            )
        )

    def crm_create(self, request, queryset):
        task_ids = [crm_create.delay(str(answers.uuid)) for answers in queryset]
        tasks_run = len(task_ids)
        self.message_user(
            request,
            ngettext(
                "%d task was successfully queued.",
                "%d tasks were successfully queued.",
                tasks_run,
            )
            % tasks_run,
            messages.SUCCESS,
        )

    crm_create.short_description = "Submit Answers to CRM"
