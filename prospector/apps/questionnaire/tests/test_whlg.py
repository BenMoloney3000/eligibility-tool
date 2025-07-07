from django.test import TestCase

from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire.tests import factories


class TestWHLGEligibility(TestCase):
    def test_flagged_for_private_rental_f_band(self):
        answers = factories.AnswersFactory(
            tenure=enums.Tenure.RENTED_PRIVATE,
            sap_band=enums.EfficiencyBand.F,
        )

        assert answers.is_whlg_prs_sap_f_or_g is True

    def test_whlg_all_eligibility_routes(self):
        answers = factories.AnswersFactory(
            tenure=enums.Tenure.OWNER_OCCUPIED,
            sap_band=enums.EfficiencyBand.D,
            multiple_deprivation_index=1,
            means_tested_benefits=True,
            household_income=35000,
            household_income_after_tax=35000,
            housing_costs=1000,
            adults=2,
            children=1,
        )

        expected = {
            "Pathway 1: IMD:ID 1-2",
            "Pathway 2: Means-Tested Benefits",
            "Pathway 3: Income < £36k",
            "Pathway 3: AHC Equalisation",
        }

        assert set(answers.whlg_all_eligibility_routes) == expected
