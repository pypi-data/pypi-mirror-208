#!/usr/bin/env python
# coding: utf-8

##
# @file
# @brief DS_Preprocessor base class for Preprocess class.

from typing import List, Any
from gaiaframework.base.common.component import DS_Component
from gaiaframework.base.pipeline.predictables.predictable import DS_Predictable
from gaiaframework.base.pipeline.artifacts.shared_artifacts import DS_SharedArtifacts

class DS_Preprocessor(DS_Component):
    """! DS_Preprocessor the base class for Preprocess class.

    This is the first stage of the pipeline and its main goal is to prepare our dataset format to the model.
    """

    def __init__(self, artifacts:DS_SharedArtifacts=None):
        """! DS_Preprocessor initializer

        Args:
            artifacts(DS_SharedArtifacts): Shared artifacts instance.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)
        self.input = None

    def __call__(self, **kwargs: Any) -> Any:
        """! DS_Preprocessor.preprocess __call__ method. It is called when its instance gets called ().

        Args:
            **kwargs: Data loaded initially to run model on.
        Returns:
            List[DS_Predictable]: Result of execute method with **kwargs as parameter.
        """
        return self.execute(**kwargs)

    def normalize_input(self, **kwargs: Any) -> Any:
        """! DS_Preprocessor.normalize_input base method. Implemented in generatedProjectNamePreprocess class."""
        raise NotImplementedError

    def preprocess(self, raw_input:Any):
        """! DS_Preprocessor.preprocess,
        Override method in generatedProjectNamePreprocess class and return a list of predictable objects.


        Args:
            raw_input: Data loaded initially to run model on.

        Returns:
            List[DS_Predictable] - Not implemented yet.

        Raises:
            NotImplementedError

        """
        raise NotImplementedError
        ## Should return a list of predictable objects

    def execute(self, **kwargs: Any) -> List[DS_Predictable]:
        """! Executes preprocess stage.

        Args:
            **kwargs: Data loaded initially to run model on.
        Returns:
            List[DS_Predictable]: List of predictable objects
        """
        self.input = self.normalize_input(**kwargs)
        return self.preprocess(self.input)

