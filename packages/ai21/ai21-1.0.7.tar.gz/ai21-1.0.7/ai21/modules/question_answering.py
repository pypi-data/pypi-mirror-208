from ai21.constants import SAGEMAKER_ENDPOINT_KEY
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Answer(NLPTask):
    MODULE_NAME = 'answer'

    @classmethod
    def execute(cls, **params):
        validate_mandatory_field(key='context', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        validate_mandatory_field(key='question', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        use_sm_endpoint = SAGEMAKER_ENDPOINT_KEY in params
        if use_sm_endpoint:
            return cls.execute_sm_endpoint(**params)
        raise NotImplementedError(f'The module {cls.MODULE_NAME} is not implemented for the non experimental endpoint')
