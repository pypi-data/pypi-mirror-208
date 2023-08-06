import json

from ai21.ai21_studio_client import AI21StudioClient
from ai21.modules.resources.ai21_module import AI21Module
from ai21.utils import validate_mandatory_field, validate_unsupported_field


class NLPTask(AI21Module):

    @classmethod
    def execute(cls, task_url, **params):
        client = AI21StudioClient(**params)
        return client.execute_http_request(method='POST', url=task_url, params=params)

    @classmethod
    def execute_sm_endpoint(cls, mandatory_fields=None, unsupported_fields=None, **params):
        endpoint_name = params.pop('sm_endpoint')
        call_name = f'Sagemaker {endpoint_name}'
        if mandatory_fields is not None:
            for mandatory_field in mandatory_fields:
                validate_mandatory_field(mandatory_field, call_name, params)
        if unsupported_fields is not None:
            for unsupported_field in unsupported_fields:
                validate_unsupported_field(key=unsupported_field, call_name=call_name, params=params)
        input_json = json.dumps(params)
        from ai21.SM_utils import invoke_sm_endpoint  # import here because boto3 exists only in SM mode
        return invoke_sm_endpoint(endpoint_name, input_json)
