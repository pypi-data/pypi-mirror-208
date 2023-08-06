#!/usr/bin/env python
# coding: utf-8

##
# @file
# @brief DS_Postprocessor base class for Postprocess class.

from typing import List, Any
from gaiaframework.base.common.component import DS_Component
from gaiaframework.base.pipeline.predictables.predictable import DS_Predictable
from gaiaframework.base.pipeline.artifacts.shared_artifacts import DS_SharedArtifacts

class DS_Postprocessor(DS_Component):
    """! DS_Postprocessor the base class for Postprocess class."""

    def __init__(self, artifacts:DS_SharedArtifacts=None) -> None:
        """! DS_Postprocessor initializer

        Args:
            artifacts(DS_SharedArtifacts): Shared artifacts instance.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)

    def normalize_output(self, predictables:List[DS_Predictable]) -> Any:
        """! DS_Postprocessor.normalize_output base method.

        Not implemented, override in generatedProjectNamePostprocess class.

        It should return final results output as a generatedProjectNameOutputs datatype object.

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def execute(self,  predictables:List[Any], **kwargs: Any) -> Any:
        """! DS_Postprocessor.execute - executes postprocess stage.

        Args:
            predictables:List[Any]: List of predictables received from the model and/or forcer.
        Returns:
            List[Outputs]: List of results after post-processing.
        """
        return self.normalize_output(super().execute(predictables))
