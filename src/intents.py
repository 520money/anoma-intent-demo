from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Intent:
    """Base intent describing a user's desired outcome rather than concrete steps.

    Attributes:
        name: Human-readable name of the intent.
        params: Structured parameters describing the desired outcome.
        tags: Optional labels to help match to solvers/capabilities.
        priority: Higher means more important/urgent.
    """

    name: str
    params: Dict[str, Any]
    tags: Optional[List[str]] = None
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Capability:
    """A capability that can satisfy certain intents.

    Attributes:
        name: Capability identifier.
        accepts_tags: Tags this capability is designed to handle.
        required_params: Parameter keys required to execute successfully.
    """

    name: str
    accepts_tags: List[str]
    required_params: List[str]

    def score_breakdown(self, intent: Intent) -> Dict[str, Any]:
        """Return detailed scoring breakdown for explainability."""
        tag_overlap = 0.0
        if intent.tags:
            tag_overlap = len(set(self.accepts_tags) & set(intent.tags)) / max(
                1, len(set(intent.tags))
            )

        present_params = [k for k in self.required_params if k in intent.params]
        missing_params = [k for k in self.required_params if k not in intent.params]
        params_score = len(present_params) / max(1, len(self.required_params))

        # Increase weight for params to favor correct capability when params match
        total = 0.3 * tag_overlap + 0.7 * params_score
        return {
            "capability": self.name,
            "total": total,
            "tag_overlap": tag_overlap,
            "params_score": params_score,
            "required_params": list(self.required_params),
            "present_params": present_params,
            "missing_params": missing_params,
        }

    def score(self, intent: Intent) -> float:
        return float(self.score_breakdown(intent)["total"])


class IntentRegistry:
    """In-memory registry of intents and capabilities."""

    def __init__(self) -> None:
        self._intents: List[Intent] = []
        self._capabilities: List[Capability] = []

    # Intents
    def add_intent(self, intent: Intent) -> None:
        self._intents.append(intent)

    def list_intents(self) -> List[Intent]:
        return list(self._intents)

    # Capabilities
    def add_capability(self, capability: Capability) -> None:
        self._capabilities.append(capability)

    def list_capabilities(self) -> List[Capability]:
        return list(self._capabilities)

    # Matching
    def find_best_capability(self, intent: Intent) -> Optional[Capability]:
        if not self._capabilities:
            return None
        ranked = self.rank_capabilities(intent)
        if not ranked:
            return None
        best_score, best_cap = ranked[0]
        if best_score <= 0.0:
            return None
        return best_cap

    def rank_capabilities(self, intent: Intent) -> List[Tuple[float, Capability]]:
        """Return capabilities ranked by score (desc)."""
        scored: List[Tuple[float, Capability]] = [
            (capability.score(intent), capability) for capability in self._capabilities
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def explain_capabilities(self, intent: Intent) -> List[Dict[str, Any]]:
        """Return detailed breakdowns sorted by total score."""
        details = [capability.score_breakdown(intent) for capability in self._capabilities]
        details.sort(key=lambda d: d["total"], reverse=True)
        return details


