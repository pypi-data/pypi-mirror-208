from typing import List

from ai21 import Completion
from ai21.constants import SAGEMAKER_ENDPOINT_KEY
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Experimental(NLPTask):

    @classmethod
    def _execute(cls, module: str, **params):
        url = f'{cls.get_base_url(**params)}/experimental/{module}'
        return super().execute(task_url=url, **params)

    @classmethod
    def rewrite(cls, **params):
        validate_mandatory_field(key='text', call_name="rewrite_experimental", params=params, validate_type=True, expected_type=str)
        url = cls.get_base_url(**params)
        url = f'{url}/experimental/rewrite'
        return super().execute(task_url=url, **params)

    @classmethod
    def summarize(cls, **params):
        validate_mandatory_field(key='text', call_name="summarize_experimental", params=params, validate_type=True, expected_type=str)
        url = cls.get_base_url(**params)
        url = f'{url}/experimental/summarize'
        return super().execute(task_url=url, **params)

    @classmethod
    def embed(cls, **params):
        validate_mandatory_field(key='texts', call_name="embed_experimental", params=params, validate_type=True, expected_type=list)
        url = cls.get_base_url(**params)
        url = f'{url}/experimental/embed'
        return super().execute(task_url=url, **params)

    @classmethod
    def j1_grande_instruct(cls, **params):
        params["model"] = "j1-grande-instruct"
        return Completion.execute(experimental_mode=True, **params)

    @classmethod
    def answer(cls, **params):
        validate_mandatory_field(key='context', call_name="answer_experimental", params=params, validate_type=True, expected_type=str)
        validate_mandatory_field(key='question', call_name="answer_experimental", params=params, validate_type=True, expected_type=str)
        use_sm_endpoint = SAGEMAKER_ENDPOINT_KEY in params
        if use_sm_endpoint:
            return cls.execute_sm_endpoint(**params)
        url = cls.get_base_url(**params)
        url = f'{url}/experimental/answer'
        return super().execute(task_url=url, **params)
