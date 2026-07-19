from pathlib import Path

import pytest

from factory_creator.evolution.fitness_aspects import FitnessAspect
from factory_creator.util.reflection import Reflection, ReflectionError


def write_plugin(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)


def test_reflection_discovers_recursive_external_subclasses(tmp_path):
    write_plugin(
        tmp_path / "nested" / "custom.py",
        "from factory_creator.evolution.fitness_aspects import FitnessAspect\n"
        "class CustomAspect(FitnessAspect):\n"
        "    def evaluate(self, context): return 7\n",
    )
    discovered = Reflection.discover_subclasses(FitnessAspect, tmp_path)
    assert [item.display_name for item in discovered] == ["CustomAspect"]
    assert discovered[0].identifier == "internal:nested/custom.py:CustomAspect"


def test_reflection_does_not_duplicate_imported_class(tmp_path):
    write_plugin(
        tmp_path / "first.py",
        "from factory_creator.evolution.fitness_aspects import FitnessAspect\n"
        "class FirstAspect(FitnessAspect):\n"
        "    def evaluate(self, context): return 1\n",
    )
    write_plugin(tmp_path / "second.py", "from .first import FirstAspect\n")
    discovered = Reflection.discover_subclasses(FitnessAspect, tmp_path)
    assert [item.display_name for item in discovered] == ["FirstAspect"]
    assert discovered[0].identifier == "internal:first.py:FirstAspect"


def test_reflection_rejects_required_constructor_argument(tmp_path):
    write_plugin(
        tmp_path / "invalid.py",
        "from factory_creator.evolution.fitness_aspects import FitnessAspect\n"
        "class InvalidAspect(FitnessAspect):\n"
        "    def __init__(self, required): pass\n"
        "    def evaluate(self, context): return 1\n",
    )
    with pytest.raises(ReflectionError, match="parameterless constructor"):
        Reflection.discover_subclasses(FitnessAspect, tmp_path)
