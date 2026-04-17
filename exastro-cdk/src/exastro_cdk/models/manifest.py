from dataclasses import dataclass, field
from typing import Any


@dataclass
class MovementModel:
    name: str
    description: str = ""


@dataclass
class ManifestModel:
    project_id: str
    conductor: dict[str, Any] = field(default_factory=dict)
    movements: list[MovementModel] = field(default_factory=list)
