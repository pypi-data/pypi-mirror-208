# AI21 Studio Client
Python client for the AI21 Studio API

## API Keys
API key can be set globally, using ai21.api_key, or alternatively - be passed to any function call 
as a named argument. For example - ai21.Dataset.get(api_key=api_key)

## Installation:
`pip install -U ai21`

## Client customization
The ai21 namespace has parameters that one can set globally, and they will 
be used by all the following client calls. 
One can also pass each of these parameters as a named argument. 
If a parameter is overridden globally, and also passed as a named argument - 
the passed named argument will be used with the following client calls.
The supported parameters are described below:
```text
* api_key (str) - the key to be used for the Authorization header
* organization (str) - this information is sent as part of the user-agent
* application (str) - this information is sent as part of the user-agent
* api_version (str) - the api version. (i.e. v1 / v2). Default=v1
* api_host (str) - the api host. Default=https://api.ai21.com
* timeout_sec (int) - the number of seconds the client must wait before cutting the connection. Default=30
* num_retries (int) - the number of attempts to retry a failure response. Default=0 (no retries)
* log_level (str) - debug / info / error (Default=error)
```
### Retry on Failure
By default, there is no retry on failures. If setting the num_retries parameter
to an integer greater than 0, then all the following client calls will retry up to the specified 
number of times on the following http error codes: 429, 500, 503.

### Documentation & resources
https://studio.ai21.com/docs

## Usage

### Studio API
In the following example, an AI21 API client is used with an API key and a timeout parameter set globally. 
This example uses a simple completion call with only prompt and maxTokens arguments supplied
(all other completion settings are set to their defaults):
```python
ai21.api_key = 'my_api_key'
ai21.timeout_sec = 20
response = ai21.Completion.execute(model="j1-large", prompt="hello world", maxTokens=20)
print(response)
```

### SageMaker Endpoint
This python SDK can also be used to invoke Jurassic models as a SageMaker (SM) endpoint. To activate this option, make sure to install with the extra SM dependencies:

`pip install -U ai21['SM']`

You can then generate a completion by running:
```python
response = ai21.Completion.execute(sm_endpoint="<your_endpoint_name>", prompt="hello world", maxTokens=20)
print(response)
```