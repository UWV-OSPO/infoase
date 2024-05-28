import os
from uwv_toolkit.utils import load_env
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings


def azure_llm(**kwargs):

    load_env()

    verbose = os.environ.get("VERBOSE", "0") == "1"

    return AzureChatOpenAI(
        openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment_name=os.environ["AZURE_DEPLOYMENT_NAME"],
        model=os.environ["AZURE_OPENAI_MODEL_NAME"],
        verbose=verbose,
        model_kwargs={"seed": 1},
        **kwargs,
    )


def azure_embeddings(**kwargs):
    load_env()
    return AzureOpenAIEmbeddings(
        openai_api_key=os.environ["EMBEDDINGS_AZURE_OPENAI_API_KEY"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=os.environ["EMBEDDINGS_AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["EMBEDDINGS_AZURE_OPENAI_DEPLOYMENT"],
        **kwargs,
    )
