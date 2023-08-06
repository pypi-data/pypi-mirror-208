from crossmark_jotform_api.jotForm import JotForm, JotFormSubmission
import pytest

def test_some_function():
    API_KEY = "4a637cfb2a68c0715390481bdfce9172"
    FORM_ID = "230046700095144"
    myClass = JotForm(API_KEY, FORM_ID)
    assert myClass is not None
