import pytest

from src import queries


class DummyIngredient:
    def __init__(self, name: str, ingredient_id: int):
        self.name = name
        self.ingredient_id = ingredient_id


class DummyAssoc:
    def __init__(self, ingredient: DummyIngredient, is_removable: bool):
        self.ingredient = ingredient
        self.ingredient_id = ingredient.ingredient_id
        self.is_removable = is_removable


class DummyOffering:
    def __init__(self, associations):
        self.ingredients = associations


def test_classify_removal_requests_handles_mixed_inputs():
    tomato = DummyAssoc(DummyIngredient("Tomato", 1), True)
    basil = DummyAssoc(DummyIngredient("Basil", 2), False)
    offering = DummyOffering([tomato, basil])

    removable, missing, locked = queries._classify_removal_requests(
        offering,
        ["Tomato", "tomatoes", "Basil", "", "Tomato"]
    )

    assert removable == [tomato]
    assert missing == ["tomatoes"]
    assert locked == ["Basil"]


def test_classify_removal_requests_is_case_insensitive_and_deduplicates():
    olive = DummyAssoc(DummyIngredient("Olive Oil", 3), True)
    offering = DummyOffering([olive])

    removable, missing, locked = queries._classify_removal_requests(
        offering,
        ["olive oil", "OLIVE OIL", "Olive  Oil"]
    )

    assert removable == [olive]
    assert missing == []
    assert locked == []
