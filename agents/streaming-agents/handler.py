# save the below code in a file by name handler.py
# Importing the necessary packages
from typing import Any, Dict, List

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult

# Creating the custom callback handler class


class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, queue) -> None:
        super().__init__()
        # we will be providing the streamer queue as an input
        self._queue = queue
        # defining the stop signal that needs to be added to the queue in
        # case of the last token
        self._stop_signal = None
        print("Custom handler Initialized")

    # On the arrival of the new token, we are adding the new token in the
    # queue
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self._queue.put(token)

    # on the start or initialization, we just print or log a starting message
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        print("generation started")

    # On receiving the last token, we add the stop signal, which determines
    # the end of the generation
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        print("\n\ngeneration concluded")
        self._queue.put(self._stop_signal)


# class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
#     def _init_(self, user_id: str, session_id: str, user_input: str, chat_history: list) -> None:
#         super()._init_()
#         self.total_tokens = 0
#         self.content = ""

#         self.chat_history = chat_history

#     async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
#         # adding the tokens to the queue for streaming
#         self.content += token
#         self.queue.put_nowait(token)

#     async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
#         # to stream even after the completion of one LLM cycle if it did not stream anything
#         if self.content != "":
#             # calculate the number of tokens on output promptt)
#             message = {"Human": self.user_input, "AI": self.content}
#             data_to_be_stored = {
#                 "message": message,
#             ]
#             return await super().on_llm_end(response, **kwargs)
