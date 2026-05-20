from dataclasses import dataclass, field
from typing import Any


@dataclass
class MovementModel:
    """Movementの定義モデル."""

    name: str
    description: str = ""
    orchestrator: str = "ansible_role"
    host_specific_format: str = "IP"  # "IP" or "ホスト名" (TODO)
    movement_id: str | None = None


@dataclass
class ManifestModel:
    """マニフェストの定義モデル."""

    workspace_id: str
    conductor: dict[str, Any] = field(default_factory=dict)
    movements: list[MovementModel] = field(default_factory=list)
