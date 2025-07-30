import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        SECRET_KEY="test",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "prospector.apps.questionnaire",
            "prospector.apps.parity",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        USE_TZ=True,
        TIME_ZONE="UTC",
    )
    django.setup()

import sys
import types

crm_tasks = types.ModuleType("prospector.apps.crm.tasks")
def crm_create(*args, **kwargs):
    return None
crm_tasks.crm_create = crm_create
crm_module = types.ModuleType("prospector.apps.crm")
crm_module.tasks = crm_tasks
sys.modules["prospector.apps.crm"] = crm_module
sys.modules["prospector.apps.crm.tasks"] = crm_tasks

from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire.tests.factories import AnswersFactory
from prospector.apps.questionnaire.views.trail import RecommendedMeasures


def test_solar_pv_and_battery_added():
    answers = AnswersFactory.build(roof_construction=enums.RoofConstruction.PNLA)
    view = RecommendedMeasures()
    view.answers = answers
    measures = view.determine_recommended_measures()
    assert measures == [
        {
            "type": enums.PossibleMeasures.SOLAR_PV_INSTALLATION,
            "label": enums.PossibleMeasures.SOLAR_PV_INSTALLATION.label,
        },
        {
            "type": enums.PossibleMeasures.BATTERY_STORAGE,
            "label": enums.PossibleMeasures.BATTERY_STORAGE.label,
        },
    ]
