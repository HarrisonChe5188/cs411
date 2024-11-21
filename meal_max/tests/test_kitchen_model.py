from contextlib import contextmanager
import re
import sqlite3
import os

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

# Helper function to normalize SQL queries
def normalize_whitespace(sql_query: str) -> str:
        return re.sub(r'\s+', ' ', sql_query).strip()

# Mock database connection fixture
@pytest.fixture
def mock_cursor(mocker):
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_conn.commit.return_value = None

        @contextmanager
        def mock_get_db_connection():
                yield mock_conn

        mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)
        return mock_cursor

######################################################
# Add and Delete Tests
######################################################

def test_create_meal(mock_cursor):
    """Test creating a meal"""
    create_meal(meal="Pasta", cuisine="Italian", price=10.0, difficulty="LOW")

    expected_query = normalize_whitespace("""
                INSERT INTO meals (meal, cuisine, price, difficulty)
                VALUES (?, ?, ?, ?)
        """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Pasta", "Italian", 10.0, "LOW")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with duplicate name (should raise an error)"""    
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")
    with pytest.raises(ValueError, match="Meal with name 'Pasta' already exists"):
        create_meal(meal="Pasta", cuisine="Italian", price=10.0, difficulty="LOW")

def test_create_meal_invalid_price():
    """Test creating a meal with invalid price"""
    with pytest.raises(ValueError, match="Invalid price: -5.0"):
        create_meal(meal="Pasta", cuisine="Italian", price=-5.0, difficulty="LOW")
    
    with pytest.raises(ValueError, match="Invalid price: invalid"):
        create_meal(meal="Pasta", cuisine="Italian", price="invalid", difficulty="LOW")

def test_create_meal_invalid_difficulty():
    """Test creating a meal with invalid difficulty"""
    with pytest.raises(ValueError, match="Invalid difficulty level: EXTREME"):
        create_meal(meal="Pasta", cuisine="Italian", price=10.0, difficulty="EXTREME")
    with pytest.raises(ValueError, match="Invalid difficulty level: invalid"):
        create_meal(meal="Pasta", cuisine="Italian", price=10.0, difficulty="invalid")

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meals table"""
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))
    clear_meals()

    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the table by meal id"""
    mock_cursor.fetchone.return_value = [False]
    delete_meal(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_delete_meal_bad_id(mock_cursor):
    """Test soft deleting a meal from the table by non-existent meal id"""

    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test soft deleting a meal that's already marked as deleted"""

    mock_cursor.fetchone.return_value = [True]
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)

######################################################
# Get Tests
######################################################

def test_get_leaderboard_wins(mock_cursor):
    """Test fetching leaderboard through wins"""
    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 10.0, "LOW", 5, 3, 0.6),
        (2, "Sushi", "Japanese", 15.0, "MED", 4, 4, 1.0)
    ]
    leaderboard = get_leaderboard("wins")
    expected = [
        {'id': 1, 'meal': "Pasta", 'cuisine': "Italian", 'price': 10.0, 'difficulty': "LOW", 'battles': 5, 'wins': 3, 'win_pct': 60.0},
        {'id': 2, 'meal': "Sushi", 'cuisine': "Japanese", 'price': 15.0, 'difficulty': "MED", 'battles': 4, 'wins': 4, 'win_pct': 100.0}
    ]

    assert leaderboard == expected, f"Expected {expected}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
                SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
                FROM meals WHERE deleted = false AND battles > 0
                ORDER BY wins DESC
        """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_win_pct(mock_cursor):
    """Test fetching leaderboard through win percentage"""
    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 10.0, "LOW", 5, 3, 0.6),
        (2, "Sushi", "Japanese", 15.0, "MED", 4, 4, 1.0)
    ]
    leaderboard = get_leaderboard("win_pct")
    expected = [
        {'id': 1, 'meal': "Pasta", 'cuisine': "Italian", 'price': 10.0, 'difficulty': "LOW", 'battles': 5, 'wins': 3, 'win_pct': 60.0},
        {'id': 2, 'meal': "Sushi", 'cuisine': "Japanese", 'price': 15.0, 'difficulty': "MED", 'battles': 4, 'wins': 4, 'win_pct': 100.0}
    ]

    assert leaderboard == expected, f"Expected {expected}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
                SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
                FROM meals WHERE deleted = false AND battles > 0
                ORDER BY win_pct DESC
        """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_bad_param(mock_cursor):
    """Test fetching leaderboard when sort_by parameter is invalid"""

    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard(sort_by="invalid")

def test_get_meal_by_id(mock_cursor):
    """Test getting meal by its id""" 
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "LOW", False)
    result = get_meal_by_id(1)
    expected = Meal(id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty="LOW")
    assert result == expected, f"Expected {expected}, got {result}"
  
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    """Test getting a meal by a non-existent id"""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_id_already_deleted_id(mock_cursor):
    """Test getting a meal by an already deleted id"""
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "LOW", True)

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)

def test_get_meal_by_name(mock_cursor):
    """Test getting a meal by name"""
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "LOW", False)
    
    # Call the function under test
    result = get_meal_by_name("Pasta")
    
    # Create the expected result
    expected = Meal(id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty="LOW")
    
    # Assert the result is as expected
    assert result == expected, f"Expected {expected}, got {result}"

    # Normalize and assert the SQL query used
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, deleted
        FROM meals WHERE meal = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Assert that the SQL query was executed with the correct arguments
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ('Pasta',)  

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}"

def test_get_meal_by_name_already_deleted_name(mock_cursor):
    """Test getting an already deleted meal by its name"""

    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "LOW", True)
    with pytest.raises(ValueError, match="Meal with name Pasta has been deleted"):
        get_meal_by_name("Pasta")

def test_get_meal_by_name_bad_name(mock_cursor):
    """Test getting a meal by a name that doesn't exist"""

    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with name Steak not found"):
        get_meal_by_name("Steak")


######################################################
# Update Tests
######################################################

def test_update_meal_stats_win(mock_cursor):
    """Test updating meal stats if a meal wins"""
    mock_cursor.fetchone.return_value = [False]
    update_meal_stats(1, "win")
    expected = normalize_whitespace("""UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?""")
    actual = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual == expected, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected}, got {actual}."

def test_update_meal_stats_loss(mock_cursor):
    """Test updating meal stats if a meal loses"""

    mock_cursor.fetchone.return_value = [False]
    update_meal_stats(1, "loss")
    expected = ("""UPDATE meals SET battles = battles + 1 WHERE id = ?""")
    actual = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual == expected, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected}, got {actual}."

def test_update_meal_stats_bad_id(mock_cursor):
    """Test updating meal stats if a non-existent meal"""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        update_meal_stats(999, "win")
    
def test_update_meal_stats_deleted_id(mock_cursor):
    """Test updating meal stats on a soft deleted meal"""
    mock_cursor.fetchone.return_value = [True]
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))

def test_update_meal_stats_invalid_result(mock_cursor):
    """Test updating meal stats on a meal with an invalid match result"""
    mock_cursor.fetchone.return_value = [False]
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(1, "draw")

