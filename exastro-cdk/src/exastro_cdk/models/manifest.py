from dataclasses import dataclass, field
from typing import Any


@dataclass
class MovementModel:
    """Movementの定義モデル."""

    name: str
    description: str = ""
    orchestrator: str = "ansible_legacy"


@dataclass
class ManifestModel:
    """マニフェストの定義モデル."""

    workspace_id: str
    conductor: dict[str, Any] = field(default_factory=dict)
    movements: list[MovementModel] = field(default_factory=list)
