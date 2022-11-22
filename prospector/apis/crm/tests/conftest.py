import pytest

from prospector.apps.questionnaire.tests import factories


@pytest.fixture()
def answers():
    def get_answers(**kwargs):
        return factories.AnswersFactory(**kwargs)

    return get_answers
