"""! @brief Pipeline entry point."""
import asyncio
from pipeline.pipeline import generatedProjectNamePipeline


##
# @file
#
# @brief Pipeline entry point.
if __name__ == '__main__':
    ## Creates an instance of the pipeline
    p = generatedProjectNamePipeline()

    ## This method executes the pipeline, dataset and required params can be loaded here.\n
    # Examples:
    # @code
    # data = {}
    # for file in data_files:
    #     with open(file) as f:
    #         data = load_json(f)
    #
    # output = p.execute(**data)
    # @endcode
    # or
    # @code
    # p.execute(data=mydata)
    # @endcode
    # or
    # @code
    # sig = Signature(uid=1, text=signature, hints=None)
    # output = p.execute(signatures=[sig])
    # @endcode
    # Define data passed through the execute method in the schema/<my-new-project>Inputs.py class, for example:
    # @code
    # class <my-new-project>Inputs(BaseModel):
    #     signatures: List[Signature]
    # @endcode
    # or
    # @code
    # class <my-new-project>Inputs(BaseModel):
    #     data = {}
    # @endcode

    output = p.execute()
    print(output)


    # for streaming
    # output = p.execute_stream()
    # async def stream_response():
    #     count = 0
    #     final_text = ''
    #     async for chunk in output:
    #         count += 1
    #         final_text = chunk['text']
    #         print('final_text', final_text)
    #
    #
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(stream_response())
