import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

"""Fixtures providing sample meal combatants for the tests."""
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

def test_battle_with_two_combatants(battle_model, sample_combatants):
    """Test conducting a battle with two combatants."""
    battle_model.combatants = sample_combatants
    winner = battle_model.battle()

    assert winner in [sample_combatants[0].meal, sample_combatants[1].meal], "The winner should be one of the combatants"
    assert len(battle_model.combatants) == 1, "Only one combatant should remain after the battle"
    assert battle_model.combatants[0].meal == winner, "The winner should be the only remaining combatant"

def test_battle_randomly_determined_winner(battle_model):
    """Test that battle can result in either combatant winning in a close battle scenario."""
    meal1 = Meal(1, 'Spicy Curry', 'Indian', 15.0, "MED")
    meal2 = Meal(2, 'Pasta', 'Italian', 15.0, "MED")
    battle_model.combatants = [meal1, meal2]
    
    # Conduct multiple battles to see variation in winners
    results = {meal1.meal: 0, meal2.meal: 0}
    for _ in range(10):
        battle_model.combatants = [meal1, meal2]
        winner = battle_model.battle()
        results[winner] += 1

    assert results[meal1.meal] > 0 and results[meal2.meal] > 0, "Both meals should win at least once in multiple rounds"

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
    assert score == expected_score, f"Expected score to be {expected_score}, but got {score}"

def test_get_battle_score_low_difficulty(battle_model, sample_meal2):
    """Test score calculation with a low difficulty modifier."""
    score = battle_model.get_battle_score(sample_meal2)
    expected_score = (sample_meal2.price * len(sample_meal2.cuisine)) - 3
    assert score == expected_score, f"Expected score to be {expected_score}, but got {score}"

##################################################
# Combatant Management Test Cases
##################################################

def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing the combatants list after adding a combatant."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_prep_combatant_addition(battle_model, sample_meal1, sample_meal2):
    """Test adding combatants to the battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2, "There should be exactly two combatants"

def test_prep_combatant_maximum_exceeded(battle_model, sample_meal1, sample_meal2):
    """Test that adding a third combatant raises ValueError."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)
