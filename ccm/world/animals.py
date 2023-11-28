from enum import Enum


class Animal(Enum):
    def __init__(self, display_name: str) -> None:
        self.display_name = display_name

    def __str__(self) -> str:
        return self.display_name

    HUMAN = "human"
    CHICKEN = "chicken"
    SHRIMP = "shrimp"
    CARP = "carp"
    BSF = "bsf"


_name_to_animal = {}
# Initialize _name_to_animal based on Enum entries
for animal in Animal:
    _name_to_animal[animal.display_name] = animal


def get_animal_by_name(name: str) -> Animal:
    if name not in _name_to_animal:
        raise ValueError(f"No supported animal of name: {name}")
    return _name_to_animal[name]
