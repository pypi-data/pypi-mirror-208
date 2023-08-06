
from ai21.errors import EmptyMandatoryListException
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Improvements(NLPTask):
    MODULE_NAME = 'improvements'

    @classmethod
    def execute(cls, **params):
        validate_mandatory_field(key='text', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        if params.get('types') is None or len(params['types']) == 0:
            raise EmptyMandatoryListException('types')
        url = cls.get_base_url(**params)
        url = f'{url}/{cls.MODULE_NAME}'
        return super().execute(task_url=url, **params)
