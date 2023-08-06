# !/usr/bin/env python
# coding: utf-8

from typing import List, Any

from gaiaframework.base.pipeline.preprocessor import DS_Preprocessor
from ..schema.inputs import generatedProjectNameInputs
from ..schema.outputs import generatedProjectNameOutputs
from ..artifacts.shared_artifacts import generatedProjectNameSharedArtifacts

##
# @file
# @brief Preprocess class, implements DS_Preprocessor base class.
class generatedClass(DS_Preprocessor):
    """! Preprocessor class implements DS_Preprocessor base class.

    This is the first stage of the pipeline and its main goal is to prepare our dataset format to the model.

    Its base class DS_Preprocessor declares phases based on UVM (Universal Verification Methodology) and by this
    gives us a structured way to work in each one of the main components by overriding and implementing those phases
    in this class.

    Important note:
    Those methods are divided into two groups, the ones that run from the __init__() and
    those that run from the execute() method, use them based on the required execution order.

    In the __init__() we have the following called:
    - build
    - config
    - config_from_json
    - connect

    In the execute(), we call the following:
    - reset
    - pre_run
    - run
    - post_run
    - evaluate
    """

    def __init__(self, artifacts: generatedProjectNameSharedArtifacts=None):
        """! generatedClass (Preprocess) initializer

        Args:
            artifacts(generatedProjectNameSharedArtifacts): Shared artifacts instance.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)

    def normalize_input(self, **kwargs: Any) -> generatedProjectNameInputs:
        """! Converts dataset to generatedProjectNameInputs

        Args:
            **kwargs: Loaded dataset.
        Returns:
            The loaded dataset in generatedProjectNameInputs datatype.
        """
        return generatedProjectNameInputs(**kwargs)

    def config(self):
        """! Config method called from DS_Component.__init__()

        Method not implemented, ready for your implementation, see more information in class description.
        """
        pass

    def connect(self):
        """! Connect method called from DS_Component.__init__().

        Method not implemented, ready for your implementation, see more information in class description.
        """

        ##
        #@hidecallgraph @hidecallergraph

        super().connect()

    def reset(self, text: str = '', hints: List[Any] = []):
        """! Reset data members, called from DS_Component.execute() method.

        Method not implemented, ready for your implementation, see more information in class description.

        Args:
            text: str
            hints: List[Any]
        """

        ##
        # For example:
        # @code {.py}
        # def reset(self, text: str, raw_input: Any):
        #
        #     self.text = ""
        #     self.hints = raw_input.hints
        #
        # @endcode

        pass

    def get_from_regex(self):
        """! Get a predefined key from common/regex_handler.py

        Method not implemented, ready for your implementation.
        """
        ##
        # For example:
        # @code{.py}
        # from gaiaframework.base.common import RegexHandler
        #
        # def get_from_regex(self):
        #    return RegexHandler.url.findall("")
        # @endcode

        pass

    def preprocess(self, raw_input: Any):
        """! Implement method to return a list of predictable objects in generatedProjectNameInputs datatype.

        Args:
            raw_input: Data loaded initially to run model on.

        Returns:
            raw_input: Not implemented yet.

        Raises:
            NotImplementedError
        """

        ##
        # For example, minimum return as-is:
        # @code{.py}
        # def preprocess(self, raw_input: Any):
        #     return raw_input
        # @endcode

        raise NotImplementedError
