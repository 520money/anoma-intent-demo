from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from .intents import Intent
from .solver import default_registry_and_solver


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Intent-centric demo CLI")
    parser.add_argument("name", help="Intent name, e.g. transfer or notify")
    parser.add_argument("--param", action="append", default=[], help="key=value param (repeatable)")
    parser.add_argument("--tag", action="append", default=[], help="tag label (repeatable)")
    parser.add_argument("--json", action="store_true", help="output result as JSON")
    parser.add_argument("--explain", action="store_true", help="show capability ranking and breakdown")
    return parser.parse_args()


def parse_params(param_items: List[str]) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    for item in param_items:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        # best-effort numeric parse
        try:
            if "." in value:
                params[key] = float(value)
            else:
                params[key] = int(value)
            continue
        except ValueError:
            pass
        params[key] = value
    return params


def main() -> int:
    args = parse_args()
    params = parse_params(args.param)

    registry, solver = default_registry_and_solver()

    # map common aliases to tags
    alias_to_tags = {
        "transfer": ["transfer", "payment"],
        "pay": ["transfer", "payment"],
        "notify": ["notify", "message"],
        "message": ["notify", "message"],
    }

    intent = Intent(name=args.name, params=params, tags=(args.tag or alias_to_tags.get(args.name, [])))

    if args.explain:
        explained = solver.solve_with_explain(intent)
        if args.json:
            payload = {"intent": intent.to_dict(), **explained}
            print(json.dumps(payload, ensure_ascii=False))
        else:
            result_text = explained.get("result")
            chosen = explained.get("chosen_capability")
            ranking = explained.get("ranking", [])
            if result_text is None:
                print("No capability found or handler missing for this intent.")
            else:
                print(result_text)
            print("\nExplain:")
            print(f"  chosen: {chosen}")
            for i, d in enumerate(ranking[:5], start=1):
                print(
                    f"  {i}. {d['capability']}: total={d['total']:.2f}, tags={d['tag_overlap']:.2f}, params={d['params_score']:.2f}"
                )
    else:
        result = solver.solve(intent)
        if args.json:
            payload = {"intent": intent.to_dict(), "result": result}
            print(json.dumps(payload, ensure_ascii=False))
        else:
            if result is None:
                print("No capability found or handler missing for this intent.")
            else:
                print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


