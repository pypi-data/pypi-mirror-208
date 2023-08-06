from gaiaframework.base.cloud_eval.cloud_eval_client_base import CloudEvalClientBase
from tester.evaluator import generatedProjectNameEvaluator

UNIMPLEMENTED_ERROR_MESSAGE = "Please override the parent base class methods for using cloud eval"


class CloudEvalClient(CloudEvalClientBase):
    def __init__(self):
        self.model_evaluator = generatedProjectNameEvaluator()
    """
    Override the parent base class methods for using cloud eval
    """
    def get_request_headers(self, row: dict):
        raise NotImplementedError(UNIMPLEMENTED_ERROR_MESSAGE)

    def get_request_payload(self, row: dict):
        raise NotImplementedError(UNIMPLEMENTED_ERROR_MESSAGE)

    def extract_model_predictions_from_response(self, predictions):
        raise NotImplementedError(UNIMPLEMENTED_ERROR_MESSAGE)

    def get_endpoint_name(self):
        raise NotImplementedError(UNIMPLEMENTED_ERROR_MESSAGE)

    def evaluate_model_results(self, row: dict):
        raise NotImplementedError(UNIMPLEMENTED_ERROR_MESSAGE)

    def set_format_output(self, row: dict):
        raise NotImplementedError(UNIMPLEMENTED_ERROR_MESSAGE)
