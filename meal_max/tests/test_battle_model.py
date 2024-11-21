import pytest
from unittest.mock import MagicMock
from contextlib import contextmanager
import re

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, update_meal_stats

# Helper function to normalize SQL queries
def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mock database connection fixture
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = [False] 
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)
    return mock_cursor

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_meal1():
    return Meal(1, 'Food 1', 'Cuisine 1', 20.0, "HIGH")

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Food 2', 'Cuisine 2', 5.0, "LOW")

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

##################################################
# Battle Management Test Cases
##################################################

def test_battle_with_two_combatants(mock_cursor, battle_model, sample_combatants):
    """Test conducting a battle with two combatants."""
    battle_model.combatants = sample_combatants
    winning_meal_name = battle_model.battle()  # Get the name of the winning meal
    
    # Identify the winner object in sample_combatants based on the returned meal name
    winner = next(combatant for combatant in sample_combatants if combatant.meal == winning_meal_name)

    # Ensure the winner is in the list and the only remaining combatant
    assert winner.meal in [combatant.meal for combatant in sample_combatants], "Winner should be one of the combatants."
    assert len(battle_model.combatants) == 1, "Only one combatant should remain after the battle."
    assert battle_model.combatants[0] == winner, "The winner should be the only remaining combatant."

    # Verify the SQL update queries for both the winner and loser
    expected_select_query = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    actual_select_query = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    assert actual_select_query == expected_select_query, "The SELECT query did not match the expected structure."
    assert mock_cursor.execute.call_args_list[0][0][1] == (winner.id,), f"Expected {winner.id} as argument for the SELECT query but got {mock_cursor.execute.call_args_list[0][0][1]}."

    # Verify the second query to update battle stats
    expected_update_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")
    actual_update_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_update_query == expected_update_query, "The UPDATE query did not match the expected structure."
    assert mock_cursor.execute.call_args_list[1][0][1] == (winner.id,), f"Expected {winner.id} as argument for the UPDATE query but got {mock_cursor.execute.call_args_list[1][0][1]}."

def test_battle_with_insufficient_combatants(battle_model, sample_meal1):
    """Test that a ValueError is raised if there are fewer than two combatants."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()

##################################################
# Score Calculation Test Cases
##################################################

def test_get_battle_score_high_difficulty(battle_model, sample_meal1):
    """Test score calculation with a high difficulty modifier."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 1
    assert score == expected_score, f"Expected score: {expected_score}, got: {score}"

def test_get_battle_score_low_difficulty(battle_model, sample_meal2):
    """Test score calculation with a low difficulty modifier."""
    score = battle_model.get_battle_score(sample_meal2)
    expected_score = (sample_meal2.price * len(sample_meal2.cuisine)) - 3
    assert score == expected_score, f"Expected score: {expected_score}, got: {score}"

##################################################
# Combatant Management Test Cases
##################################################

def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing the combatants list after adding a combatant."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing."

def test_prep_combatant_addition(battle_model, sample_meal1, sample_meal2):
    """Test adding combatants to the battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2, "There should be exactly two combatants."

def test_prep_combatant_maximum_exceeded(battle_model, sample_meal1, sample_meal2):
    """Test that adding a third combatant raises ValueError."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)
