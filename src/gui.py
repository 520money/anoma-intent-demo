from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List

from .intents import Intent
from .solver import default_registry_and_solver


class IntentApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Intent Demo (Desktop)")
        self.geometry("760x560")

        self.registry, self.solver = default_registry_and_solver()

        # Inputs
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Intent name").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar(value="transfer")
        ttk.Entry(frm, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=tk.EW)

        ttk.Label(frm, text="Tags (comma)").grid(row=1, column=0, sticky=tk.W)
        self.tags_var = tk.StringVar(value="transfer,payment")
        ttk.Entry(frm, textvariable=self.tags_var, width=40).grid(row=1, column=1, sticky=tk.EW)

        ttk.Label(frm, text="Params (key=value per line)").grid(row=2, column=0, sticky=tk.NW)
        self.params_txt = tk.Text(frm, height=10, width=60)
        self.params_txt.grid(row=2, column=1, sticky=tk.EW)
        self.params_txt.insert("1.0", "to=alice\namount=10")

        self.explain_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Explain", variable=self.explain_var).grid(row=3, column=1, sticky=tk.W, pady=(6,0))

        run_btn = ttk.Button(frm, text="Run Intent", command=self.on_run)
        run_btn.grid(row=4, column=1, sticky=tk.W, pady=10)

        # Output
        ttk.Label(frm, text="Result").grid(row=5, column=0, sticky=tk.NW)
        self.result_txt = tk.Text(frm, height=2, width=60)
        self.result_txt.grid(row=5, column=1, sticky=tk.EW)

        ttk.Label(frm, text="Intent JSON").grid(row=6, column=0, sticky=tk.NW)
        self.intent_txt = tk.Text(frm, height=6, width=60)
        self.intent_txt.grid(row=6, column=1, sticky=tk.EW)

        ttk.Label(frm, text="Explain (ranking)").grid(row=7, column=0, sticky=tk.NW)
        self.explain_txt = tk.Text(frm, height=12, width=60)
        self.explain_txt.grid(row=7, column=1, sticky=tk.EW)

        frm.columnconfigure(1, weight=1)

        # Preset buttons
        preset_frame = ttk.Frame(frm)
        preset_frame.grid(row=8, column=1, sticky=tk.W, pady=10)
        ttk.Button(preset_frame, text="Preset: transfer", command=self.fill_transfer).pack(side=tk.LEFT, padx=4)
        ttk.Button(preset_frame, text="Preset: notify", command=self.fill_notify).pack(side=tk.LEFT, padx=4)
        ttk.Button(preset_frame, text="Preset: swap", command=self.fill_swap).pack(side=tk.LEFT, padx=4)

    def parse_params(self, text: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        for raw in text.splitlines():
            line = raw.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip()
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

    def on_run(self) -> None:
        name = self.name_var.get().strip()
        tags_str = self.tags_var.get().strip()
        tags: List[str] = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        params = self.parse_params(self.params_txt.get("1.0", tk.END))

        if not tags:
            alias_to_tags = {
                "transfer": ["transfer", "payment"],
                "pay": ["transfer", "payment"],
                "notify": ["notify", "message"],
                "message": ["notify", "message"],
                "swap": ["swap", "trade"],
            }
            tags = alias_to_tags.get(name, [])

        intent = Intent(name=name, params=params, tags=tags)

        if self.explain_var.get():
            explained = self.solver.solve_with_explain(intent)
            result_text = explained.get("result")
            self.result_txt.delete("1.0", tk.END)
            self.result_txt.insert(tk.END, result_text or "No capability found.")
            self.intent_txt.delete("1.0", tk.END)
            self.intent_txt.insert(tk.END, json.dumps(intent.to_dict(), ensure_ascii=False, indent=2))
            self.explain_txt.delete("1.0", tk.END)
            self.explain_txt.insert(tk.END, json.dumps(explained.get("ranking", []), ensure_ascii=False, indent=2))
        else:
            result_text = self.solver.solve(intent)
            self.result_txt.delete("1.0", tk.END)
            self.result_txt.insert(tk.END, result_text or "No capability found.")
            self.intent_txt.delete("1.0", tk.END)
            self.intent_txt.insert(tk.END, json.dumps(intent.to_dict(), ensure_ascii=False, indent=2))
            self.explain_txt.delete("1.0", tk.END)
            self.explain_txt.insert(tk.END, "(Explain disabled)")

    def fill_transfer(self) -> None:
        self.name_var.set("transfer")
        self.tags_var.set("transfer,payment")
        self.params_txt.delete("1.0", tk.END)
        self.params_txt.insert("1.0", "to=alice\namount=10")

    def fill_notify(self) -> None:
        self.name_var.set("notify")
        self.tags_var.set("notify,message")
        self.params_txt.delete("1.0", tk.END)
        self.params_txt.insert("1.0", "to=bob\ntext=hello")

    def fill_swap(self) -> None:
        self.name_var.set("swap")
        self.tags_var.set("swap,trade")
        self.params_txt.delete("1.0", tk.END)
        self.params_txt.insert("1.0", "from_token=ETH\nto_token=USDC\namount=1")


def main() -> int:
    app = IntentApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


