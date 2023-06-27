import pytest

from . import factories
from prospector.apps.questionnaire import enums
from prospector.apps.questionnaire import utils


@pytest.mark.django_db
def test_get_income_rating():
    """Test get_Income_rating.

    is dependant on the following fields (all effectively boolean):

        answers.total_income_lt_31k,
        answers.take_home_lt_31k:
            enums.IncomeIsUnderThreshold.choices
                YES = "YES", "Yes, it's under that figure"
                NO = "NO", "No, it's over that figure"
                UNKNOWN = "UNKNOWN", "I don't know"

        answers.disability_benefits,
        answers.child_benefit,
        answers.income_lt_child_benefit_threshold
            Boolean

    has RAYG rating output
    """

    def to_income_choices(value):
        return {
            True: enums.IncomeIsUnderThreshold.YES,
            False: enums.IncomeIsUnderThreshold.NO,
            None: enums.IncomeIsUnderThreshold.UNKNOWN,
        }[value]

    def get_test_vector(
        total_income_lt_31k,
        take_home_lt_31k,
        disability_benefits,
        child_benefit,
        income_lt_child_benefit_threshold,
    ):
        return factories.AnswersFactory(
            total_income_lt_31k=to_income_choices(total_income_lt_31k),
            take_home_lt_31k=to_income_choices(take_home_lt_31k),
            disability_benefits=disability_benefits,
            child_benefit=child_benefit,
            income_lt_child_benefit_threshold=income_lt_child_benefit_threshold,
        )

    # Expected outputs
    income_ratings = {
        enums.RAYG.RED: [get_test_vector(False, False, False, False, True)],
        enums.RAYG.AMBER: [],
        enums.RAYG.YELLOW: [],
        enums.RAYG.GREEN: [],
    }

    for expected_result, test_vectors in income_ratings.items():
        for test_vector in test_vectors:
            assert expected_result == utils.get_income_rating(test_vector)
