from ai21.constants import SAGEMAKER_ENDPOINT_KEY
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Summarize(NLPTask):
    MODULE_NAME = 'summarize'

    @classmethod
    def execute(cls, **params):
        validate_mandatory_field(key='sourceType', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        validate_mandatory_field(key='source', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        use_sm_endpoint = SAGEMAKER_ENDPOINT_KEY in params
        if use_sm_endpoint:
            return cls.execute_sm_endpoint(**params)
        url = cls.get_base_url(**params)
        url = f'{url}/{cls.MODULE_NAME}'
        return super().execute(task_url=url, **params)
