from typing import Union, List

import logging
import sys
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
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from pipeline.pipeline import generatedProjectNamePipeline
from pipeline.schema.inputs import generatedProjectNameInputs
from pipeline.schema.outputs import generatedProjectNameOutputs
from tester.test_schema.test_input import TestInputRequest
from tester.test_schema.test_output import TestOutputResponse
from tester.general_tester import generatedProjectNameGeneralTester


async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token": # todo: please replace with realistic token
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


app = FastAPI()

origins = load_allowed_cors_origins()
methods = ["*"]
headers = ["*"]
credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=credentials,
    allow_methods=methods,
    allow_headers=headers,
)

pipeline = generatedProjectNamePipeline()
# from server.pool import InstancePool
# pipelines = [generatedProjectNamePipeline() for i in range(3)]
# app.pipelines = InstancePool(pipelines)


@app.post('/predict', dependencies=[Depends(get_token_header)])
def predict(body: generatedProjectNameInputs, request: Request) -> List[generatedProjectNameOutputs]:
    '''
    predict api
    '''
    data = body.dict()
    # logger.info({"message": "predict invoked", "data": json.dumps(data)})
    # print('data', data)

    # call model here
    try:
        output: generatedProjectNameOutputs = pipeline.execute(**data)
        logger.info("INFO predict invoked", extra={"input": data, "output": output.dict()})
    except Exception as ex:
        logger.exception(msg=data, exc_info=True)
        output = {'error': {'request': ex}}
        logger.error("ERROR predict invoked", extra={"input": data, "output": output})
    # call model here
    return output


@app.post('/parse', dependencies=[Depends(get_token_header)])
def parse(body: generatedProjectNameInputs, request: Request) -> List[generatedProjectNameOutputs]:
    '''
    parse api
    '''
    data = body.dict()
    # logger.info({"message": "parse invoked", "data": json.dumps(data)})
    # print('data', data)

    # call model here
    try:
        output: generatedProjectNameOutputs = pipeline.execute(**data)
        logger.info("INFO parse invoked", extra={"input": data, "output": output.dict()})
    except Exception as ex:
        logger.exception(msg=data, exc_info=True)
        output = {'error': {'request': ex}}
        logger.error("ERROR parse invoked", extra={"input": data, "output": output})
    # call model here
    return output


# Fetch the proper tester for the project
model_tester = generatedProjectNameGeneralTester()

@app.post('/chat', dependencies=[Depends(get_token_header)])
async def chat(body: generatedProjectNameInputs, request: Request) -> StreamingResponse:
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

@app.post('/test', dependencies=[Depends(get_token_header), Depends(verify_env)], include_in_schema=False)
def test(input_request: TestInputRequest) -> List[TestOutputResponse]:
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


@app.get("/livenessprobe")
def liveness_probe():
    return {"alive": True}


@app.get("/readinessprobe")
def readiness_probe():
    return {"ready": True}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

