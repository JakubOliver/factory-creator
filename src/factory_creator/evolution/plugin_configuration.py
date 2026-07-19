from dataclasses import dataclass
from pathlib import Path

from .fitness_aspects import FitnessAspect
from .mutations.mutation import Mutation
from ..util.reflection import DiscoveredClass, Reflection


@dataclass
class MutationConfiguration:
    identifier: str
    enabled: bool = True
    start_generation: int = 0
    end_generation: int | float = float("inf")


@dataclass
class FitnessAspectConfiguration:
    identifier: str
    enabled: bool = True
    weight: int | float = 1


class PluginConfiguration:
    EVOLUTION_DIRECTORY = Path(__file__).resolve().parent
    MUTATIONS_DIRECTORY = EVOLUTION_DIRECTORY / "mutations"
    FITNESS_ASPECTS_DIRECTORY = EVOLUTION_DIRECTORY / "fitness_aspects"

    @staticmethod
    def discover_mutations(
        user_directory: str | None = None,
    ) -> list[DiscoveredClass[Mutation]]:
        return Reflection.discover_subclasses(
            Mutation,
            PluginConfiguration.MUTATIONS_DIRECTORY,
            user_directory,
            Mutation.__module__.rsplit(".", 1)[0],
        )

    @staticmethod
    def discover_fitness_aspects(
        user_directory: str | None = None,
    ) -> list[DiscoveredClass[FitnessAspect]]:
        return Reflection.discover_subclasses(
            FitnessAspect,
            PluginConfiguration.FITNESS_ASPECTS_DIRECTORY,
            user_directory,
            FitnessAspect.__module__.rsplit(".", 1)[0],
        )

    @staticmethod
    def create_mutations(
        discovered: list[DiscoveredClass[Mutation]],
        configurations: dict[str, MutationConfiguration] | None = None,
    ) -> list[Mutation]:
        result = []
        configurations = configurations or {}

        for item in discovered:
            mutation = item.create()
            config = configurations.get(item.identifier)

            if config is not None and not config.enabled:
                continue

            if config is not None:
                mutation.start_generation = config.start_generation
                mutation.end_generation = config.end_generation

            result.append(mutation)

        return result

    @staticmethod
    def create_fitness_aspects(
        discovered: list[DiscoveredClass[FitnessAspect]],
        configurations: dict[str, FitnessAspectConfiguration] | None = None,
    ) -> list[FitnessAspect]:
        result = []
        configurations = configurations or {}

        for item in discovered:
            aspect = item.create()
            config = configurations.get(item.identifier)

            if config is not None and not config.enabled:
                continue

            if config is not None:
                aspect.weight = config.weight

            result.append(aspect)
            
        return result
