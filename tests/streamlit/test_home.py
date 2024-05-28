import os
import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from tests.base_pytest import login_streamlit_authenticator
from streamlit.testing.v1 import AppTest


@pytest.fixture
def at() -> AppTest:
    return AppTest.from_file("./src/Home.py")


def test_load_page(at: AppTest):
    at.run()
    assert not at.exception


def test_load_page_no_status(at: AppTest):
    at.run()

    # check there is st.success and st.error
    assert not at.success
    assert not at.error
