#!/usr/bin/env python
# coding: utf-8

import json
from gaiaframework.base.pipeline.artifacts.shared_artifacts import DS_SharedArtifacts

class generatedClass(DS_SharedArtifacts):

    def __init__(self) -> None:
        super().__init__()

    def extend_load_file_type(self, file_type, path, absolute_path, name):
        if absolute_path:
            if file_type == 'your-file-type':
                with open(absolute_path) as json_file:
                    setattr(self, name, json.load(json_file))
