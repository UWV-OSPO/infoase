from uwv_toolkit.utils import azure_llm
from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler
from langchain_core.prompts import PromptTemplate
from typing import Dict, Any, Optional
from uuid import UUID
from langchain.globals import set_debug

set_debug(True)


def test_callbacks():
    llm = azure_llm(temperature=0)

    config = RunnableConfig(callbacks=[StdOutCallbackHandler()])
    prompt = PromptTemplate.from_template(
        "What is a good name for a company that makes {product}?"
    )

    # in two lines
    runnable = prompt | llm
    runnable = runnable.with_config(config)

    import sys
    from io import StringIO

    # Create a StringIO object to capture stdout
    stdout_capture = StringIO()
    sys.stdout = stdout_capture

    # Invoke the runnable
    runnable.invoke(input={"product": "colorful socks"})

    # Get the captured stdout as a string
    stdout_string = stdout_capture.getvalue()

    # Reset stdout to its original value
    sys.stdout = sys.__stdout__

    # Print the captured stdout
    print("!!!!!!!!!!!!!!!!!!!!!!!!")
    print(stdout_string)


# def test_custom_callback():
#     class CustomCallbackHandler(BaseCallbackHandler):

#         def on_chain_end(
#             self,
#             outputs: Dict[str, Any],
#             *,
#             run_id: UUID,
#             parent_run_id: Optional[UUID] = None,
#             **kwargs: Any,
#         ) -> Any:
#             print(f"Custom callback: {outputs}")

#     llm = azure_llm(temperature=0)

#     config = RunnableConfig(callbacks=[CustomCallbackHandler()])
#     prompt = PromptTemplate.from_template(
#         "What is a good name for a company that makes {product}?"
#     )

#     # in two lines
#     runnable = prompt | llm
#     runnable = runnable.with_config(config)

#     runnable.invoke(input={"product": "colorful socks"})
