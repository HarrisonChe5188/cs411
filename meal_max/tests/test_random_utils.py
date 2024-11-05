random utils
import pytest
import requests

from meal_max.utils.random_utils import get_random

@pytest.fixture()
def random_utils():
    return get_random

@pytest.fixture
def mock_random_org(mocker):
    mock_response = mocker.Mock()
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random(random_utils):
    result = random_utils() 
    assert isinstance(result, float)

def test_get_random_request_failure(mocker, random_utils):
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        random_utils() 

def test_get_random_timeout(mocker,random_utils):
    """Simulate  a timeout."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        random_utils()

def test_get_random_invalid_response(mock_random_org,random_utils):
    mock_random_org.text = "invalid_response"

    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        random_utils()