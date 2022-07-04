from django.test import TestCase

from . import factories
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import models
from prospector.apps.questionnaire import services


def test_fake_epc_gets_processed():
    """Test that the fake EPC gets processed.

    A bit artificial to get the coverage where it needs to be, and better than
    nothing!
    """

    answers = services.prepopulate_from_epc(
        factories.AnswersFactory.build(), factories.FAKE_EPC
    )

    assert answers.property_type_orig == enums.PropertyType.BUNGALOW
    assert answers.property_form_orig == enums.PropertyForm.SEMI_DETACHED
    assert answers.property_age_band_orig == enums.PropertyAgeBand.FROM_1976
    assert answers.wall_type_orig == enums.WallType.CAVITY
    assert answers.walls_insulated_orig is True
    assert answers.suspended_floor_orig is False
    assert answers.unheated_loft_orig is False
    assert answers.room_in_roof_orig is False
    assert answers.rir_insulated_orig is False
    assert answers.roof_space_insulated_orig is False
    assert answers.flat_roof_orig is True
    assert answers.gas_boiler_present_orig is False
    assert answers.trvs_present_orig == enums.TRVsPresent.NONE
    assert answers.room_thermostat_orig is False
    assert answers.ch_timer_orig is True
    assert answers.programmable_thermostat_orig is None
    assert answers.other_heating_present_orig is True
    assert answers.heat_pump_present_orig is False
    assert answers.other_heating_fuel_orig is enums.NonGasFuel.ELECTRICITY
    assert answers.storage_heaters_present_orig is False
    assert answers.has_solar_pv_orig is True


class TestSyncingAdults(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.answers = factories.AnswersFactory()

    def setUp(self):
        models.HouseholdAdult.objects.filter(answers=self.answers).delete()

    def test_three_are_created_from_none(self):

        self.answers.adults = 3
        services.sync_household_adults(self.answers)

        assert models.HouseholdAdult.objects.filter(answers=self.answers).count() == 3

        assert (
            models.HouseholdAdult.objects.filter(
                answers=self.answers, adult_number=1
            ).count()
            == 1
        )

        assert (
            models.HouseholdAdult.objects.filter(
                answers=self.answers, adult_number=2
            ).count()
            == 1
        )

        assert (
            models.HouseholdAdult.objects.filter(
                answers=self.answers, adult_number=3
            ).count()
            == 1
        )

    def test_three_are_reduced_to_one(self):

        adult_one = factories.HouseholdAdultFactory(
            answers=self.answers, adult_number=1
        )
        adult_two = factories.HouseholdAdultFactory(
            answers=self.answers, adult_number=2
        )
        adult_three = factories.HouseholdAdultFactory(
            answers=self.answers, adult_number=3
        )

        self.answers.adults = 1
        services.sync_household_adults(self.answers)

        assert models.HouseholdAdult.objects.filter(answers=self.answers).count() == 1

        adult_one.refresh_from_db()

        with self.assertRaises(models.HouseholdAdult.DoesNotExist):
            adult_two.refresh_from_db()

        with self.assertRaises(models.HouseholdAdult.DoesNotExist):
            adult_three.refresh_from_db()


class TestSyncingBenefits(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.answers = factories.AnswersFactory()
        cls.household_adult = factories.HouseholdAdultFactory(answers=cls.answers)

    def setUp(self):
        models.WelfareBenefit.objects.filter(recipient=self.household_adult).delete()

    def test_five_are_created_from_none(self):
        self.household_adult.uc = "True"
        self.household_adult.income_support = "True"
        self.household_adult.working_tax_credit = "True"
        self.household_adult.carers_allowance = "True"
        self.household_adult.pension_credit = "True"

        services.sync_benefits(self.household_adult)

        assert (
            models.WelfareBenefit.objects.filter(recipient=self.household_adult).count()
            == 5
        )

        assert models.WelfareBenefit.objects.filter(
            recipient=self.household_adult,
            benefit_type=enums.BenefitType.UC.value,
        ).exists()

        assert models.WelfareBenefit.objects.filter(
            recipient=self.household_adult,
            benefit_type=enums.BenefitType.INCOME_SUPPORT.value,
        ).exists()

        assert models.WelfareBenefit.objects.filter(
            recipient=self.household_adult,
            benefit_type=enums.BenefitType.WORKING_TAX_CREDIT.value,
        ).exists()

        assert models.WelfareBenefit.objects.filter(
            recipient=self.household_adult,
            benefit_type=enums.BenefitType.CARERS_ALLOWANCE.value,
        ).exists()

        assert models.WelfareBenefit.objects.filter(
            recipient=self.household_adult,
            benefit_type=enums.BenefitType.PENSION_CREDIT.value,
        ).exists()

    def test_two_are_reduced_to_one_different_one(self):
        first_benefit = models.WelfareBenefit.objects.create(
            recipient=self.household_adult,
            benefit_type=enums.BenefitType.INCOME_SUPPORT.value,
        )
        second_benefit = models.WelfareBenefit.objects.create(
            recipient=self.household_adult,
            benefit_type=enums.BenefitType.CHILD_BENEFIT.value,
        )

        self.household_adult.pip = "True"

        services.sync_benefits(self.household_adult)

        assert (
            models.WelfareBenefit.objects.filter(recipient=self.household_adult).count()
            == 1
        )

        with self.assertRaises(models.WelfareBenefit.DoesNotExist):
            first_benefit.refresh_from_db()

        with self.assertRaises(models.WelfareBenefit.DoesNotExist):
            second_benefit.refresh_from_db()

        assert models.WelfareBenefit.objects.filter(
            recipient=self.household_adult,
            benefit_type=enums.BenefitType.PIP.value,
        ).exists()
