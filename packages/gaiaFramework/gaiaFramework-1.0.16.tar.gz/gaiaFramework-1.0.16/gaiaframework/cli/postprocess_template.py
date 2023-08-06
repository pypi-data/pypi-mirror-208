 # !/usr/bin/env python
# coding: utf-8

##
# @file
# @brief Postprocessor class, implemented DS_Postprocessor base.

from gaiaframework.base.pipeline.predictables.predictable import DS_Predictable
from typing import List, Union

from gaiaframework.base.pipeline.postprocessor import DS_Postprocessor
from ..artifacts.shared_artifacts import generatedProjectNameSharedArtifacts
from ..schema.outputs import generatedProjectNameOutputs


class generatedClass(DS_Postprocessor):
    """generatedClass class (Postprocessor) implements DS_Postprocessor base class.
    It is the last stage of the pipeline, its main focus is to return the results in the required format.
    """

    def __init__(self, artifacts: generatedProjectNameSharedArtifacts=None) -> None:
        """! generatedClass class (Postprocessor) initializer

        Args:
            artifacts(generatedProjectNameSharedArtifacts): Shared artifacts instance.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)

    def config(self):
        """Implement here configurations required on Preprocess stage. Overrides DS_Component.config()"""
        pass

    def normalize_output(self, predictables: Union[DS_Predictable, List[DS_Predictable]]) -> Union[generatedProjectNameOutputs, List[generatedProjectNameOutputs]]:
        """! Converts received predictable objects to generatedProjectNameOutputs datatype.

        Args:
            predictables: List[DS_Predictable] - Predictable objects, the results from the model.

        Returns:
            generatedProjectNameOutputs: List[generatedProjectNameOutputs] - Results converted to Outputs format.
        """

        output: generatedProjectNameOutputs = ''
        isList = isinstance(predictables, list)
        if isList:
            output: List[generatedProjectNameOutputs] = []
        if isList:
            if predictables and len(predictables):
                for item in predictables:
                    output.append(self.get_output_object(item))
        else:
            output = self.get_output_object(predictables)
        return output

    def get_output_object(self, predictable):
        """! Parse a single predictable item, needs to be implemented.

        Args:
            predictable: DS_Predictable - Single predictable object.

        Returns:
            generatedProjectNameOutputs: generatedProjectNameOutputs - Parsed results

        Raises:
            NotImplementedError

        """

        ##
        # Implementation example:
        # @code{.py}
        # prob = predictable[-1]
        # pred = False
        #
        # if prob > self.artifacts.threshold:
        #     pred = True
        # return generatedProjectNameOutputs(pred=pred, prob=prob, version=self.artifacts.version)
        # @endcode

        # for streaming chat
        # from gaiaframework.base.common.async_iterator import AsyncIterator
        # import json
        # results = AsyncIterator()
        # count = 0
        # final_text = ''
        # while count < 4:
        #     final_text += f"test_{count}"
        #     count += 1
        #     if count < 4:
        #         final_text += ' '
        #     results.add_item(json.dumps({"text": final_text}))
        # return results

        raise NotImplementedError

