import hashlib
import importlib
import importlib.util
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Generic, TypeVar


T = TypeVar("T")


class ReflectionError(RuntimeError):
    ...


@dataclass(frozen=True)
class DiscoveredClass(Generic[T]):
    identifier: str
    class_type: type[T]
    source: Path
    external: bool = False

    @property
    def display_name(self) -> str:
        return self.class_type.__name__

    def create(self) -> T:
        return self.class_type()


class Reflection:
    @staticmethod
    def discover_subclasses(
        base_class: type[T],
        internal_directory: str | Path,
        user_directory: str | Path | None = None,
        internal_package: str | None = None,
    ) -> list[DiscoveredClass[T]]:
        discovered: dict[str, DiscoveredClass[T]] = {}

        internal_path = Path(internal_directory).resolve()

        Reflection._discover_directory(
            base_class, 
            internal_path, 
            internal_package, 
            False, 
            discovered
        )

        if user_directory and str(user_directory).strip():
            user_path = Path(user_directory).expanduser().resolve()

            Reflection._discover_directory(
                base_class, 
                user_path, 
                None, 
                True, 
                discovered
            )

        return sorted(
            discovered.values(), key=lambda item: (item.display_name, item.identifier)
        )

    @staticmethod
    def _discover_directory(
        base_class: type[T],
        directory: Path,
        package: str | None,
        external: bool,
        discovered: dict[str, DiscoveredClass[T]],
    ) -> None:
        if not directory.is_dir():
            raise ReflectionError(f"Plugin directory does not exist: {directory}")

        files = sorted(
            path for path in directory.rglob("*.py")
            if path.name != "__init__.py" and "__pycache__" not in path.parts
        )

        try:
            for path in files:
                module = Reflection._load_module(
                    path, 
                    directory, 
                    package, 
                    external
                )

                Reflection._collect_classes(
                    module, 
                    path, 
                    directory, 
                    base_class, 
                    external, 
                    discovered
                )
        except Exception as error:
            if isinstance(error, ReflectionError):
                raise

            raise ReflectionError(f"Failed to load plugin module {path}: {error}") from error

    @staticmethod
    def _load_module(
        path: Path,
        root: Path,
        package: str | None,
        external: bool,
    ) -> ModuleType:
        relative = path.relative_to(root).with_suffix("")

        if package:
            module_name = ".".join((package, *relative.parts))
            return importlib.import_module(module_name)

        # Give each external plugin directory its own stable module namespace.
        # It resolves problem with same plugin names 
        # (which is not recommended, but in user plugins possible).
        digest = hashlib.sha256(str(root).encode()).hexdigest()[:12]

        module_name = f"factory_creator_user_plugins_{digest}." + ".".join(relative.parts)
        parent_name = module_name.rpartition(".")[0]

        Reflection._ensure_namespace_packages(parent_name, root, relative.parent)

        spec = importlib.util.spec_from_file_location(module_name, path)

        if spec is None or spec.loader is None:
            raise ReflectionError(f"Cannot create an import specification for {path}")
        
        module = importlib.util.module_from_spec(spec)

        sys.modules[module_name] = module

        spec.loader.exec_module(module)

        return module

    @staticmethod
    def _ensure_namespace_packages(
        name: str, 
        root: Path, 
        relative_parent: Path
    ) -> None:
        # Create missing parent packages so relative imports work in plugins.
        parts = name.split(".")

        for index in range(1, len(parts) + 1):
            package_name = ".".join(parts[:index])

            if package_name in sys.modules:
                continue

            module = ModuleType(package_name)

            depth = max(0, index - 1)
            package_path = root.joinpath(*relative_parent.parts[:depth])

            module.__path__ = [str(package_path)]
            module.__package__ = package_name

            sys.modules[package_name] = module

    @staticmethod
    def _collect_classes(
        module: ModuleType,
        source: Path,
        root: Path,
        base_class: type[T],
        external: bool,
        discovered: dict[str, DiscoveredClass[T]],
    ) -> None:
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            # Ignore classes that this module only imported from elsewhere.
            if candidate.__module__ != module.__name__:
                continue

            if candidate is base_class or not issubclass(candidate, base_class):
                continue

            if inspect.isabstract(candidate):
                continue

            try:
                candidate()
            except TypeError as error:
                raise ReflectionError(
                    f"Plugin class {candidate.__name__} in {source} must have a "
                    f"parameterless constructor: {error}"
                ) from error
            except Exception as error:
                raise ReflectionError(
                    f"Plugin class {candidate.__name__} in {source} could not be created: {error}"
                ) from error

            relative = source.relative_to(root).as_posix()
            
            origin = "external" if external else "internal"

            # Qualname also distinguishes nested classes with the same name 
            # (which is not recommended, but in user plugins possible).
            identifier = f"{origin}:{relative}:{candidate.__qualname__}"

            discovered[identifier] = DiscoveredClass(
                identifier, 
                candidate, 
                source, 
                external
            )
