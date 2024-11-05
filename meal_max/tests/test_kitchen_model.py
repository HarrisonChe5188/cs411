from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

######################################################
#
#    Fixtures
#
######################################################
@pytest.fixture
def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(self, mock_db):
        """Stub for testing create_meal function."""
        assert True

def test_create_meal_duplicate(self, mock_db):
        """Stub for testing create_meal function when meal already exists."""
        assert True

def test_create_meal_invalid_price(self, mock_db):
        """Stub for testing create_meal function when meal has negative price."""
        assert True

def test_create_meal_invalid_difficulty(self, mock_db):
        """Stub for testing create_meal function when meal has invalid difficulty."""
        assert True

def test_clear_catalog(mock_cursor, mocker):
        """Stub for testing clear_meal function on a meal that's already been deleted."""
        assert True

def test_delete_meal(self, mock_db):
        """Stub for testing delete_meal function."""
        assert True

def test_delete_meal_bad_id(self, mock_db):
        """Stub for testing delete_meal function on a non-existent meal."""
        assert True

def test_delete_meal_already_deleted(self, mock_db):
        """Stub for testing delete_meal function on a meal that's already been deleted."""
        assert True


######################################################
#
#    Get
#
######################################################

def test_get_leaderboard(self, mock_db):
        """Stub for testing get_leaderboard function."""
        assert True

def test_get_leaderboard_bad_param(self, mock_db):
        """Stub for testing get_leaderboard function when the input is invalid."""
        assert True

def test_get_meal_by_id(self, mock_db):
        """Stub for testing get_meal_by_id function."""
        assert True

def test_get_meal_by_id_bad_id(self, mock_db):
        """Stub for testing get_meal_by_id function on a non-existent meal."""
        assert True
        
def test_get_meal_by_id_already_deleted_id(self, mock_db):
        """Stub for testing get_meal_by_id function on a meal that's been deleted."""
        assert True

def test_get_meal_by_name(self, mock_db):
        """Stub for testing get_meal_by_name function."""
        assert True

def test_get_meal_by_name_bad_name(self, mock_db):
        """Stub for testing get_meal_by_name function on a non-existent meal."""
        assert True

def test_get_meal_by_name_already_deleted_name(self, mock_db):
        """Stub for testing get_meal_by_name function a meal that's already been deleted."""
        assert True

######################################################
#
#    Update
#
######################################################

def test_update_meal_stats(self, mock_db):
        """Stub for testing update_meal_stats function."""
        assert True

def test_update_meal_stats_bad_id(self, mock_db):
        """Stub for testing update_meal_stats function on a meal that does not exist."""
        assert True

def test_update_meal_stats_deleted_id(self, mock_db):
        """Stub for testing update_meal_stats function on a meal that's already been deleted."""
        assert True

def test_update_meal_stats_invalid_result(self, mock_db):
        """Stub for testing update_meal_stats function when the result is not a win or a loss."""
        assert True