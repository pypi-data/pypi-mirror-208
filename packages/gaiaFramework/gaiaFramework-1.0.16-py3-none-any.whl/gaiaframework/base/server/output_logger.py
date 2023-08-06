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