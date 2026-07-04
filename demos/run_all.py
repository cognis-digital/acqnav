#!/usr/bin/env python3
"""Run every acqnav demo in sequence; non-zero exit if any demo fails.

Each demo is a self-contained script that must exit 0. This runner is used both
locally and in CI to prove the demos stay green.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys


def _load_and_run(path: pathlib.Path) -> int:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return int(module.main())


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    # Ensure the package is importable when run from anywhere.
    sys.path.insert(0, str(here.parent))
    demos = sorted(p for p in here.glob("demo_*.py"))
    if not demos:
        print("No demos found.", file=sys.stderr)
        return 1

    failures = []
    for demo in demos:
        print(f"\n{'#' * 72}\n# RUNNING {demo.name}\n{'#' * 72}")
        try:
            rc = _load_and_run(demo)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"!! {demo.name} raised: {exc}")
            failures.append(demo.name)
            continue
        if rc != 0:
            print(f"!! {demo.name} exited {rc}")
            failures.append(demo.name)

    print(f"\n{'=' * 72}")
    print(f"Ran {len(demos)} demos; {len(failures)} failure(s).")
    if failures:
        for f in failures:
            print(f"  FAILED: {f}")
        return 1
    print("All demos passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
