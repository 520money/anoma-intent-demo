from __future__ import annotations

from typing import Callable, Dict, Optional, Any, List

from .intents import Intent, IntentRegistry, Capability


class Solver:
    """Naive solver that maps intents to capabilities and executes handlers.

    This prototype keeps execution handlers in-memory.
    """

    def __init__(self, registry: IntentRegistry) -> None:
        self.registry = registry
        self._handlers: Dict[str, Callable[[Intent], str]] = {}

    def register_handler(self, capability_name: str, handler: Callable[[Intent], str]) -> None:
        self._handlers[capability_name] = handler

    def solve(self, intent: Intent) -> Optional[str]:
        capability = self.registry.find_best_capability(intent)
        if capability is None:
            return None
        handler = self._handlers.get(capability.name)
        if handler is None:
            return None
        return handler(intent)

    def solve_with_explain(self, intent: Intent) -> Dict[str, Any]:
        """Return result along with explainable ranking."""
        ranking_details = self.registry.explain_capabilities(intent)
        # map capability name to handler presence
        chosen_capability = None
        result_text = None

        if ranking_details:
            top = ranking_details[0]
            if float(top.get("total", 0.0)) > 0.0:
                chosen_capability = str(top.get("capability"))

        if chosen_capability:
            handler = self._handlers.get(chosen_capability)
            if handler is not None:
                result_text = handler(intent)

        return {
            "result": result_text,
            "chosen_capability": chosen_capability,
            "ranking": ranking_details,
        }


def default_registry_and_solver() -> tuple[IntentRegistry, Solver]:
    registry = IntentRegistry()
    solver = Solver(registry)

    # Example capabilities and handlers
    registry.add_capability(
        Capability(name="send_notification", accepts_tags=["notify", "message"], required_params=["to", "text"])
    )
    solver.register_handler(
        "send_notification",
        lambda intent: f"Notification to {intent.params.get('to')}: {intent.params.get('text')}",
    )

    registry.add_capability(
        Capability(name="transfer_tokens", accepts_tags=["transfer", "payment"], required_params=["to", "amount"])
    )
    solver.register_handler(
        "transfer_tokens",
        lambda intent: f"Transferred {intent.params.get('amount')} to {intent.params.get('to')} (demo)",
    )

    # New: swap capability
    registry.add_capability(
        Capability(
            name="swap_tokens",
            accepts_tags=["swap", "trade"],
            required_params=["from_token", "to_token", "amount"],
        )
    )
    solver.register_handler(
        "swap_tokens",
        lambda intent: (
            f"Swapped {intent.params.get('amount')} {intent.params.get('from_token')} "
            f"-> {intent.params.get('to_token')} (demo)"
        ),
    )

    return registry, solver


