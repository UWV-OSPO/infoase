# pylint: disable=protected-access, missing-function-docstring, missing-module-docstring
import os
import tiktoken
import pytest
import pprint
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import langchain
from langchain.cache import SQLiteCache
from langchain.schema import Document
from langchain_community.graphs.graph_document import GraphDocument
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    PyPDFLoader,
    UnstructuredHTMLLoader,
)
from src.modules.utils import Utilities
from src.modules.extraction import FewShotDataExtractor
from src.modules.utils.load_env import load_env

load_env()


langchain.llm_cache = SQLiteCache(database_path="tmp/.test_langchain.db")

TESTCASE_TEXT = """
Walter DWIGHT (Walt) Elias Disney (Chicago, 5 december 1901 – Burbank, 15 december 1966) was een Amerikaans tekenaar, filmproducent, filmregisseur, scenarioschrijver, stemacteur, animator, zakenman, entertainer, internationaal icoon en een filantroop.
Disney werd vooral bekend door zijn vernieuwingen in de animatiefilm-industrie. Als medeoprichter (samen met zijn broer Roy Oliver Disney) van The Disney Brothers Studio, later omgedoopt tot Walt Disney Productions en later naar The Walt Disney Company, werd Disney een van de bekendste filmproducenten ter wereld.
"""


@pytest.fixture(name="extractor")
def fixture_extractor():
    llm = Utilities.create_llm(
        "azure", verbose=True, temperature=0, model_kwargs={"seed": 1}
    )
    return FewShotDataExtractor(llm, verbose=(os.getenv("VERBOSE") == "1"))


def test_run(extractor):
    result = extractor.run(TESTCASE_TEXT)
    # print("\n\n\n########################################|")
    # print(result)

    # print("\n\nNODES", result[0].nodes)
    # # print(result["nodes"][1])
    # print("\n\nRELS", result[0].relationships)


def test_run_list_docx(extractor):
    filepath = "data/test/disney_test_2p.docx"
    # filepath = "data/test/short_Wetsuitleg WIA.docx"
    loader = UnstructuredWordDocumentLoader(filepath)
    data = loader.load()

    result = extractor.run_list(data)
    import pprint

    pprint.pprint(result)


def test_run_list_pdf(extractor):
    filepath = "data/test/disney_test_2p.pdf"
    loader = PyPDFLoader(filepath)
    data = loader.load_and_split()

    result = extractor.run_list(data)


def test_run_list_html(extractor):
    filepath = "data/test/disney_test_2p.html"
    loader = UnstructuredHTMLLoader(filepath)
    data = loader.load_and_split()

    print(data)
    result = extractor.run_list(data)


def test_run2(extractor):
    # result = extractor.run(TESTCASE_TEXT)
    text = """Loopt uw contract af, gaat u onvrijwillig minder uren werken of wil uw werkgever u ontslaan? Probeer dan direct ander werk te vinden. Onze website werk.nl kan u daarbij helpen.

Lukt het niet om op tijd een nieuwe baan te vinden? Dan kunt u misschien een WW-uitkering krijgen. Een WW-uitkering is een tijdelijk inkomen bij werkloosheid. Een handig hulpmiddel bij uw WW-aanvraag is het Stappenplan WW. Hierin staat wat u op welk moment voor uw WW-aanvraag moet regelen."""
    result = extractor.run(text)
    print("\n\n\n########################################|")
    print(result)
