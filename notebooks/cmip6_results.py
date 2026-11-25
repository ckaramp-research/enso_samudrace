"""CMIP6 piControl results reshaped into each figure's results layout.

``../data/cmip6.json`` holds one entry per model, keyed ``CMIP6_<model>``, so
that ``plotstyle.set_cmip6`` can register the ensemble.
"""

import json
from pathlib import Path

DATA = Path("../data")
_CMIP6: dict[str, dict] | None = None


def _load() -> dict[str, dict]:
    global _CMIP6
    if _CMIP6 is None:
        _CMIP6 = json.loads((DATA / "cmip6.json").read_text())
    return _CMIP6


def common_models() -> list[str]:
    return sorted(_load())


def core() -> dict[str, dict]:
    return {k: {"full_record": v["core"]} for k, v in _load().items()}


def feedbacks() -> dict[str, dict]:
    return {k: {"values": v["feedbacks"]} for k, v in _load().items()}


def xro() -> dict[str, dict]:
    return {k: v["xro"] for k, v in _load().items()}


def nino34() -> dict[str, dict]:
    return {k: v["nino34"] for k, v in _load().items()}


def component(name: str) -> dict[str, dict]:
    return {k: v[name] for k, v in _load().items() if name in v}


def alpha() -> dict[str, dict]:
    return {k: {"full_record": {"alpha": v["alpha"]}, "member": v["member"],
                "djf_pcs": v["djf_pcs"]} for k, v in _load().items()}
