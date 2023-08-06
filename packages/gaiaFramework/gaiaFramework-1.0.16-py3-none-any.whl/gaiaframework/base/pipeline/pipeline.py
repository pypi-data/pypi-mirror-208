#!/usr/bin/env python
# coding: utf-8

"""! @brief DS_Pipeline base class for the pipeline."""

from typing import List
from gaiaframework.base.common.component import DS_Component
from gaiaframework.base.common.streaming_generations import StreamingGenerations
from gaiaframework.base.pipeline.predictables.predictable import DS_Predictable
from gaiaframework.base.pipeline.artifacts.shared_artifacts import DS_SharedArtifacts


class DS_Pipeline():
    """! DS_Pipeline base class for the pipeline.

    Its main job is to be the base for building the pipeline components.
    """

    def __init__(self):
        """! DS_Pipeline class initializer."""
        self.components:List[DS_Component] = []
        self.predictables:List[DS_Predictable] = []
        self.artifacts = self.get_artifacts()
        self.build_pipeline()
        self.configure_pipeline()
        self.connect_pipeline()

    def get_artifacts(self):
        """! Loads and returns the artifacts and vocabs,

        This method gets overridden by its parent the generatedProjectNamePipeline.get_artifacts() method."""
        return DS_SharedArtifacts()
    
    def build_pipeline(self):
        """! This is the main place where the pipeline gets build with all of its components.

        It gets overridden by a default implementation in generatedProjectNamePipeline.build_pipeline, where its
        four main components gets instantiated:

        - generatedProjectNamePreprocess
        - generatedProjectNamePredictor
        - generatedProjectNameForcer
        - generatedProjectNamePostprocess.
        """
        raise NotImplementedError

    def configure_pipeline(self, **kwargs):
        """! To add configurations that need to take place after the build_pipeline() method.

        Override method generatedProjectNamePipeline.configure_pipeline()
        """
        pass

    def connect_pipeline(self):
        """! This method distributes Artifacts instance to all pipeline components."""
        for c in self.components:
            c.artifacts = self.artifacts

    def preprocess(self, **kwargs) -> List[DS_Predictable]:
        """! Runs in the beginning of the pipeline

        It is a base method that need be overridden in generatedProjectNamePipeline.preprocess and
        needs to include all required steps before the Predictor model.

        Args:
            **kwargs: Dataset loaded initially.
        Returns:
            List[DS_Predictable]: List of predictable objects."""
        raise NotImplementedError

    def postprocess(self, predictables, **kwargs):
        """! Runs at the end of the pipeline.

        It is a base method that need be overridden in generatedProjectNamePipeline.postprocess and
        return the list of results.

        Returns:
            List[generatedProjectNameOutputs]: List of results.
            **kwargs: Dataset loaded initially.
        """
        raise NotImplementedError


    def add_component(self, component:DS_Component):
        """! Adds a component to pipeline.

        Two components added by default: Predictor, Forcer.

        In addition to the pre-existing ones the preprocessor and postprocessor.

        Args:
            component: DS_Component, component to add.
        """
        self.components.append(component)

    def __call__(self,  **kwargs):
        """! DS_Pipeline __call__() method, runs the execute() method of this class with specified Args.

        Args:
            **kwargs: Initially loaded dataset.
        """
        return self.execute( **kwargs)

    def execute(self, **kwargs):
        """! Executes the pipeline,

        Runs the execute method for all registered components one after the other,

        Args:
            **kwargs: Initially loaded dataset.
        """
        self.predictables = self.preprocess(**kwargs)
        for c in self.components:
            self.predictables = c.execute(self.predictables)
        return self.postprocess(self.predictables)

    def execute_stream(self, **kwargs):
        """! Executes the pipeline,

        Runs the execute method for all registered components one after the other,

        Args:
            **kwargs: Initially loaded dataset.
        """
        self.predictables = self.preprocess(**kwargs)
        for c in self.components:
            self.predictables = c.execute(self.predictables)
        res = self.postprocess(self.predictables)
        return StreamingGenerations(res)
