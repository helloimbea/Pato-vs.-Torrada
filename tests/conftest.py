import pytest

from duck_vs_toast import i18n


@pytest.fixture(autouse=True)
def english():
    """Tests run in English, whatever the computer's language is."""
    i18n.set_language('en')
    yield
    i18n.set_language('en')
