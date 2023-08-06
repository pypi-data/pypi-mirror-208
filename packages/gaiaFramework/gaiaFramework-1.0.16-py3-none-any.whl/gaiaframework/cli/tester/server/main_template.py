from typing import Union, List

import logging
import sys
import time
from pythonjsonlogger import jsonlogger

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
root.addHandler(handler)

logger = logging.getLogger(__name__)

import os
import json
import uvicorn
from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from gaiaframework.base.server.server import DS_Server
from gaiaframework.base.server.output_logger import OutputLogger

from pipeline.pipeline import generatedProjectNamePipeline
from pipeline.schema.inputs import generatedProjectNameInputs
from pipeline.schema.outputs import generatedProjectNameOutputs
from tester.test_schema.test_input import TestInputRequest
from tester.test_schema.test_output import TestOutputResponse
from tester.general_tester import generatedProjectNameGeneralTester

## Initialized a pipeline for /predict /parse endpoints.
pipeline = generatedProjectNamePipeline()

# Initialize logger classes
predict_logger = OutputLogger('predict')

# Initialize a tester
model_tester = generatedProjectNameGeneralTester()

class Server(DS_Server):

    def __init__(self, debug=False):
        self.debug = debug
        self.mysql_creds = {
            'host': "localhost",
            'username': "gaia",
            'password': "1234567",
            'dbInstanceIdentifier': "gaia"
        }
        env = os.environ.get('ENV', 'dev')
        if env != 'dev':
            self.get_mysql_creds(profile_name='gaia_admin', secret="gaia_mysql_db")
        self.mysql_connect(host=self.mysql_creds['host'], user=self.mysql_creds['username'],
                           password=self.mysql_creds['password'], database=self.mysql_creds['dbInstanceIdentifier'])
        # verify_company_token=True will try to fetch company from gaia db using token
        # 'GAIA-AI-TOKEN' in headers or 'Authorization': f'Bearer {gaia_api_token}'
        # in order for it to work you must connect to mysql first using self.mysql_connect
        super().__init__(x_token="your-x-token", verify_x_token=False, verify_company_token=False)
        self.router.add_api_route("/predict", self.predict, methods=["POST"], dependencies=self.baseDependencies + [])
        self.router.add_api_route("/parse", self.parse, methods=["POST"], dependencies=self.baseDependencies + [])
        self.router.add_api_route("/chat", self.chat, methods=["POST"], dependencies=self.baseDependencies + [])
        self.router.add_api_route("/test", self.test, methods=["POST"],
                                  dependencies=self.baseDependencies + [Depends(self.verify_env)],
                                  include_in_schema=False)

    def load_allowed_cors_origins(self):
        allowed_origins = []
        cors_origin_list_path = 'server/cors_allowed_origins.json'
        if os.path.exists(cors_origin_list_path):
            with open(cors_origin_list_path) as f:
                allowed_origins = json.load(f)

        return allowed_origins

    def predict(self, body: generatedProjectNameInputs, request: Request) -> Union[generatedProjectNameOutputs, List[generatedProjectNameOutputs]]:
        """! Predict api endpoint, is designed to support predict projects such as
        scoops classification, valid user email etc.

        Use by post request, for example:

            headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
            url = http://localhost:8080/predict
            data = {}  # The data to run by model.
            response = requests.post(url, json=data, headers=headers)

        """
        host, service_account = self.extract_host_and_service_account(request)
        data = body.dict()
        self.cache_facade.get_request_data(data, host, service_account)
        predict_logger.save_request_info(data, host, service_account)

        output = self.cache_facade.get('--- REPLACE WITH KEYWORD FOR FINDING KEYS INSIDE THE INPUT (data) ---')
        if len(output) > 0:
            predict_logger.log_output(output, 'cache')
            return output
        try:
            tic = time.perf_counter()
            output: Union[generatedProjectNameOutputs, List[generatedProjectNameOutputs]] = pipeline.execute(**data)  # call model here
            pipeline_timing = f"{time.perf_counter() - tic:0.6f}"
            predict_logger.log_output(output,
                                      pipeline_timing=pipeline_timing,
                                      predictable_object_count=len(output) if isinstance(output, list) else 1)
            self.cache_facade.set(output)
        except Exception as ex:
            output = {'error': {'request': str(ex)}}
            logger.exception("ERROR predict invoked",
                             extra=dict(input=data, output=output, from_host=host, from_service_account=service_account))
        return output

    def parse(self, body: generatedProjectNameInputs, request: Request) -> Union[generatedProjectNameOutputs, List[generatedProjectNameOutputs]]:
        '''
        parse api
        '''
        data = body.dict()
        # logger.info({"message": "parse invoked", "data": json.dumps(data)})
        # print('data', data)

        # call model here
        try:
            output: Union[generatedProjectNameOutputs, List[generatedProjectNameOutputs]] = pipeline.execute(**data)
            logger.info("INFO parse invoked", extra={"input": data, "output": output.dict()})
        except Exception as ex:
            logger.exception(msg=data, exc_info=True)
            output = {'error': {'request': ex}}
            logger.error("ERROR parse invoked", extra={"input": data, "output": output})
        # call model here
        return output
    async def chat(self, body: generatedProjectNameInputs, request: Request) -> StreamingResponse:
        '''
        parse api
        '''
        data = body.dict()
        # logger.info({"message": "parse invoked", "data": json.dumps(data)})
        # print('data', data)

        # call model here
        output = pipeline.execute_stream(**data)

        async def stream_response():
            count = 0
            final_text = ''
            async for chunk in output:
                count += 1
                final_text = chunk['text']
                yield final_text

        return StreamingResponse(stream_response())
    def test(self, input_request: TestInputRequest) -> List[TestOutputResponse]:
        """
        This is the main endpoint for testing. Every project starts with a mock response service, in order to enable
        DSP integration, but as soon as a working testing functions are ready, please replace the mock service with the
        real one.

        Parameters:
            input_request: Request as received from the DSP
        Returns:
            A list of responses, to be sent back to the DSP
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


## Instantiate FastAPI()
app = FastAPI()
debug = False
server = Server(debug=debug)

## Allowed cors origins
origins = server.load_allowed_cors_origins()
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
app.include_router(server.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)