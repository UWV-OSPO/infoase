import os
import streamlit as st
from typing import Any, Dict, List
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    BaseMessage,
)
from modules.utils.load_env import load_env

load_env()


class Utilities:
    # To be able to update the changes made to modules in localhost (press r)
    @staticmethod
    def reload_module(module_name):
        import importlib
        import sys

        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        return sys.modules[module_name]

    @staticmethod
    def persistent_storage_path():
        path = os.environ.get("PERSISTENT_STORAGE_PATH", "./tmp")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def load_api_key():
        """
        Loads the OpenAI API key from the .env file or
        from the user's input and returns it
        """
        if not hasattr(st.session_state, "openai_api_key"):
            st.session_state.openai_api_key = None

        key_from_env = os.environ.get("OPENAI_API_KEY") or os.environ.get(
            "AZURE_OPENAI_API_KEY"
        )

        # you can define your API key in .env directly
        if os.path.exists(".env") and key_from_env is not None:
            openai_api_key = key_from_env
            st.sidebar.success("API key loaded from .env", icon="🚀")
        else:
            if st.session_state.openai_api_key is not None:
                openai_api_key = st.session_state.openai_api_key
                st.sidebar.success("API key loaded from previous input", icon="🚀")
            else:
                openai_api_key = st.sidebar.text_input(
                    label="#### Your OpenAI API key 👇",
                    placeholder="sk-...",
                    type="password",
                )
                if openai_api_key:
                    st.session_state.openai_api_key = openai_api_key

        return openai_api_key

    @staticmethod
    def create_llm(model_name: str, **kwargs: Any) -> BaseChatModel:
        """
        Args:
            model_name (str): The name of the chat model to create.
            **kwargs: Additional keyword arguments to pass to the chat model constructor.

        Returns:
            BaseChatModel: An instance of the specified chat model.

        Raises:
            Exception: If an invalid chat model name is provided.
        """

        if "verbose" in kwargs:
            verbose = kwargs["verbose"]
            del kwargs["verbose"]
            if verbose:
                print(f"🤖 Initiating {model_name}...")
        else:
            verbose = os.getenv("VERBOSE", "0") == "1"

        if model_name == "azure":
            return AzureChatOpenAI(
                openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
                openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                deployment_name=os.environ["AZURE_DEPLOYMENT_NAME"],
                model=os.environ["AZURE_OPENAI_MODEL_NAME"],
                verbose=verbose,
                **kwargs,
            )
        elif model_name in ("gpt-3.5-turbo", "gpt-4"):
            return ChatOpenAI(
                openai_api_key=os.environ["OPENAI_API_KEY"],
                model_name=model_name,
                verbose=verbose,
                **kwargs,
            )
        else:
            raise Exception("Invalid chat model name")
