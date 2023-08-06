from gaiaframework.base.common.component import DS_Component

##
# @file
# @brief Forcer class, implements DS_Component base class.
class generatedClass(DS_Component):
    """! Forcer class, implements DS_Component base class.

        This class was added with two main goals, to force results when:

        1. If you know certain data doesn't need to go through the model and would like to force results.
        2. Not satisfied by some results from the model and would like to force another result.

        No examples yet.
    """
    def __init__(self, artifacts=None) -> None:
        """! generatedClass (Forcer) class initializer."""

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)
