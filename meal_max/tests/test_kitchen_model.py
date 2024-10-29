from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
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

def test_delete_meal(self, mock_db):
        """Stub for testing delete_meal function."""
        assert True

######################################################
#
#    Add and delete
#
######################################################

def test_get_leaderboard(self, mock_db):
        """Stub for testing get_leaderboard function."""
        assert True

def test_get_meal_by_id(self, mock_db):
        """Stub for testing get_meal_by_id function."""
        assert True

def test_get_meal_by_name(self, mock_db):
        """Stub for testing get_meal_by_name function."""
        assert True

######################################################
#
#    Update
#
######################################################

def test_update_meal_stats(self, mock_db):
        """Stub for testing update_meal_stats function."""
        assert True