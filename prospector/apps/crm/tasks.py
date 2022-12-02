import uuid
from typing import Optional

from celery import shared_task
from celery_singleton import Singleton

from prospector.apis.crm import crm
from prospector.apps.crm.models import Answers
from prospector.apps.crm.models import CrmState


class CRMApiRequestTask(Singleton):
    _session = None

    @property
    def session(self):
        if self._session is None:
            client = crm.get_client()
            self._session = crm.get_authorised_session(client)
        return self._session


@shared_task(base=CRMApiRequestTask, bind=True, raise_on_duplicate=True)
def crm_create(self, answers_uuid: uuid.uuid4) -> Optional[dict]:
    result = None
    answers = Answers.objects.get(uuid=answers_uuid)

    # TODO: Updates not yet supported
    if answers.crmresult_set.exists():
        raise Exception("{0} already submitted".format(answers_uuid))

    try:
        result = crm.create_pcc_record(crm_create.session, crm.map_crm(answers))
    except Exception as e:
        answers.crmresult_set.create(result=result, state=CrmState.FAILURE)
        raise e  # re-raise for celery

    answers.crmresult_set.create(result=result, state=CrmState.SUCCESS)
    return result
