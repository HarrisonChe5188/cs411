from typing import List, Optional

from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPathManager:

    def __init__(self) -> None:
        paths: dict[int, MigrationPath] = {}

    def create_migration_path(self, species: str, start_location: Habitat, destination: Habitat, duration: Optional[int] = None) -> None:
        pass

    def get_migration_path_by_id(self, path_id: int) -> MigrationPath:
        pass

    def get_migration_paths(self) -> List[MigrationPath]:
        pass

    def get_migration_paths_by_destination(self, destination: Habitat) -> List[MigrationPath]:
        pass

    def get_migration_paths_by_species(self, species: str) -> List[MigrationPath]:
        pass

    def get_migration_paths_by_start_location(self, start_location: Habitat) -> List[MigrationPath]:
        pass

    def remove_migration_path(self, path_id: int) -> None:
        pass

    def update_migration_path_details(self, path_id: int, **kwargs) -> None:
        pass
