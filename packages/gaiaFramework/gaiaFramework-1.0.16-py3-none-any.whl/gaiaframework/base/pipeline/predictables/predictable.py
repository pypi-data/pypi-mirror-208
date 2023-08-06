#!/usr/bin/env python
# coding: utf-8

"""! @brief DS_Predictable base class."""

from typing import Any
from gaiaframework.base.common import DS_Object


class DS_Predictable(DS_Object):
    """! DS_Predictable base class for a single predictable object."""

    def __init__(self) -> None:
        """! Initializer for DS_Predictable
        Initializes local class variables, those predictable vars that will be transferred from component to component
        in the pipeline.
        """
        ##
        # @hidecallgraph @hidecallergraph
        super().__init__()
        self.name:str = ''
        self.input:Any = None
        self.target:Any = None    
        self.pred: Any = None
        self.prob:float = -1.0
        self.forced_pred:Any = None
        self.forced_reason:str = 'Did Not Forced'
