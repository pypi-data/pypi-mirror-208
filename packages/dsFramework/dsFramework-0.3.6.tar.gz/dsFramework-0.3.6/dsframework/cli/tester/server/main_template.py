import logging
import sys
import os
import json
import time

import uvicorn

from typing import List
from pythonjsonlogger import jsonlogger
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from starlette.requests import Request

from pipeline.pipeline import generatedProjectNamePipeline
from pipeline.schema.inputs import generatedProjectNameInputs
from pipeline.schema.outputs import generatedProjectNameOutputs
from dsframework.base.server.cache.cache import Cache
from dsframework.base.server.cache.cache_utils import CacheProvider, CacheFacade
from tester.test_schema.test_input import TestInputRequest
from tester.test_schema.test_output import TestOutputResponse
from tester.general_tester import generatedProjectNameGeneralTester

##  Logger setup
from dsframework.base.logger.pubsub_handler import PubSubHandler
from logger.config import pubsub_config


root = logging.getLogger()
root.setLevel(logging.INFO)
## Redirect logging to sys.stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
## Assign logger a json formatter to output log data as json.
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
root.addHandler(handler)

# Assign logger a pubsub handler.
is_gae = "SPRING_PROFILES_ACTIVE" in os.environ
if pubsub_config['enable'] and not is_gae:

    is_production = os.environ.get('ANY_GKE_ENV_VAR', '') == 'production'

    project_id = pubsub_config['prd_project_id'] if is_production else pubsub_config['stg_project_id']
    topic_id = pubsub_config['topic_id']

    resource = 'gae' if is_gae else 'gke'
    platform = 'prd' if is_production else 'stg'
    resource_type = resource + '-' + platform + '-' + 'original_project_name'

    handler_pubsub = PubSubHandler(project_id, topic_id, 'original_project_name', resource_type)
    handler_pubsub.name = 'handler_pubsub'
    handler_pubsub.setFormatter(formatter)
    handler_pubsub.setLevel(pubsub_config['level'])
    root.addHandler(handler_pubsub)


logger = logging.getLogger(__name__)


async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_env():
    # Don't allow usage of an endpoint on production environment
    if os.environ.get('SPRING_PROFILES_ACTIVE') == 'production':
        raise HTTPException(status_code=404, detail="Endpoint not available")


def load_allowed_cors_origins():
    allowed_origins = []
    cors_origin_list_path = 'server/cors_allowed_origins.json'
    if os.path.exists(cors_origin_list_path):
        with open(cors_origin_list_path) as f:
            allowed_origins = json.load(f)

    return allowed_origins


def extract_host_and_service_account(request):
    x_forwarded_for = request.headers.get('x-forwarded-for')
    x_goog_authenticated_user_email = request.headers.get('x-goog-authenticated-user-email')
    service_account = ''
    host = ''
    try:
        if x_goog_authenticated_user_email:
            service_account = x_goog_authenticated_user_email.replace('accounts.google.com:', '')
        if x_forwarded_for:
            host = x_forwarded_for
    except Exception as e:
        print(f'Attempt to get headers from: {request.headers} failed. Error: {e}')
        pass
    return host, service_account


class OutputLogger:
    def __init__(self, endpoint) -> None:
        self.data = None
        self.host = None
        self.service_account = None
        self.endpoint = endpoint

    def save_request_info(self, data, host, service_account) -> None:
        self.data = data
        self.host = host
        self.service_account = service_account

    def log_output(self, output, retrieve_type='', pipeline_timing=None, predictable_object_count=None):

        extra_info = dict(input=self.data, output=output, from_host=self.host,
                          from_service_account=self.service_account)
        if pipeline_timing:
            extra_info.update({"pipeline_exec_time": pipeline_timing,
                               "predictable_object_count": predictable_object_count})
        logger.info(f"INFO {self.endpoint} invoked {retrieve_type}", extra_info)


## Instantiate FastAPI()
app = FastAPI()
## Allowed cors origins
origins = load_allowed_cors_origins()
## Methods allowed, for FastAPI()
methods = ["*"]
## Headers allowed, for FastAPI()
headers = ["*"]
## Credentials required, bool.
credentials = True
##
# @var allow_origins
# Cors allowed origins.
# @var allow_credentials
# Allowed credentials by FastAPI()
# @var allow_methods
# Allowed methods by FastAPI()
# @var allow_headers
# Allowed headers by FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=credentials,
    allow_methods=methods,
    allow_headers=headers,
)

## Initialize caching - turned off by default
## To enable caching change cache_type to Cache.Type.REDIS
cache_type = Cache.Type.NONE
cache = CacheProvider.get_cache(cache_type)
cache_facade = CacheFacade(cache, cache_type)


@app.on_event("startup")
@repeat_every(seconds=60)  # 1 minute
def run_cache_timer() -> None:
    if not cache.status():
        cache.init()


## Initialized a pipeline for /predict /parse endpoints.
pipeline = generatedProjectNamePipeline()

# Initialize logger classes
predict_logger = OutputLogger('predict')


@app.post('/predict', dependencies=[Depends(get_token_header)])
def predict(body: generatedProjectNameInputs, request: Request) -> List[generatedProjectNameOutputs]:
    """! Predict api endpoint, is designed to support predict projects such as
    scoops classification, valid user email etc.

    Use by post request, for example:

        headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
        url = http://localhost:8080/predict
        data = {}  # The data to run by model.
        response = requests.post(url, json=data, headers=headers)

    """
    host, service_account = extract_host_and_service_account(request)
    data = body.dict()
    cache_facade.get_request_data(data, host, service_account)
    predict_logger.save_request_info(data, host, service_account)

    output = cache_facade.get('--- REPLACE WITH KEYWORD FOR FINDING KEYS INSIDE THE INPUT (data) ---')
    if len(output) > 0:
        predict_logger.log_output(output, 'cache')
        return output
    try:
        tic = time.perf_counter()
        output: List[generatedProjectNameOutputs] = pipeline.execute(**data)  # call model here
        pipeline_timing = f"{time.perf_counter() - tic:0.6f}"
        predict_logger.log_output(output,
                                  pipeline_timing=pipeline_timing,
                                  predictable_object_count=len(output) if isinstance(output, list) else 1)
        cache_facade.set(output)
    except Exception as ex:
        output = {'error': {'request': str(ex)}}
        logger.exception("ERROR predict invoked",
                         extra=dict(input=data, output=output, from_host=host, from_service_account=service_account))
    return output


## Fetch the proper tester for the project
model_tester = generatedProjectNameGeneralTester(pipeline)


@app.post('/test', dependencies=[Depends(get_token_header), Depends(verify_env)], include_in_schema=False)
def test(input_request: TestInputRequest) -> List[TestOutputResponse]:
    """! This is the main endpoint for testing.

        Args:
            input_request: Request as received from the DSP
        Returns:
            A list of responses, to be sent back to the DSP

    Every project starts with a default mock response service, in order to enable DSP integration (when the working
    testing functions are ready and implemented in the tester/general_tester.py),
    replace the mock service with the real one, in practice just remark the following line:

        response = model_tester.create_mock_response(input_request)

    and remove remark quotes from the following block of code:

        model_tester.save_meta_data(input_request)
        response = []
        # Until this model will support batches, work sequentially. Once it does, pass the full list of rows.
        for request_row in input_request.rows:
            input_list = [request_row]
            tester_output = model_tester.test_batch(input_list)
            response.append(tester_output[0])

    """
    response = model_tester.create_mock_response(input_request)

    """    
    model_tester.save_meta_data(input_request)
    response = []
    # Until this model will support batches, work sequentially. Once it does, pass the full list of rows.
    for request_row in input_request.rows:
        input_list = [request_row]
        tester_output = model_tester.test_batch(input_list)
        response.append(tester_output[0])
    """
    return response


@app.get("/livenessprobe")
def liveness_probe():
    """! Endpoint used to test server liveness

        Usage:
            http://localhost:8080/livenessprobe

        Returns:
            server response: {"alive": True} - On success

    """
    return {"alive": True}


@app.get("/readinessprobe")
def readiness_probe():
    """! Endpoint used to test server readiness

        Usage:
            http://localhost:8080/readinessprobe

        Returns:
            server response: {"ready": True} - On success

        """
    return {"ready": True}


if __name__ == '__main__':
    # Runs the server
    ##
    # @var host
    # IP Address
    # @var port
    # Port number
    uvicorn.run(app, host='0.0.0.0', port=8080)
