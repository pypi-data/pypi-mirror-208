from shuttlis.money import paisa_to_inr, inr_to_paisa
from shuttlis.money import to_base_denomination, from_base_denomination


def test_paisa_to_inr():
    assert paisa_to_inr(2097) == 20.97
    assert paisa_to_inr(208) == 2.08
    assert paisa_to_inr(2090) == 20.9


def test_inr_to_paisa():
    assert inr_to_paisa(20.97) == 2097
    assert inr_to_paisa(20.9) == 2090
    assert inr_to_paisa(2.08) == 208


def test_from_base_denomination():
    assert from_base_denomination(2097) == 20.97
    assert from_base_denomination(208) == 2.08
    assert from_base_denomination(2090) == 20.9


def test_to_base_denomination():
    assert to_base_denomination(20.97) == 2097
    assert to_base_denomination(20.9) == 2090
    assert to_base_denomination(2.08) == 208
