import pytest

from meal_max.models.battle_model.py import BattleModel
from meal_max.models.kitchen_model.py import Meal

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

"""Fixtures providing sample meal combatants for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Food 1', 'Cuisine 1', 2022, 20.0, "HIGH")

@pytest.fixture
def sample_Meal2():
    return Meal(2, 'Food 2', 'Cuisine 2', 2021, 5.0, "LOW")

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

##################################################
# Add Battle Management Test Cases
##################################################

def test_battle(battle_model):






def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing the entire combatants list."""
    battle_model.prep_combatant(sample_meal1)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_clear_combatants_empty(battle_model, caplog):
    """Test clearing the entire combatants list when it's empty."""
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"
    assert "Clearing an empty combatants list" in caplog.text, "Expected warning message when clearing an empty combatants list"





