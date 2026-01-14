from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agg_margins import SIMM


CONFIG_ENV_VAR = "ISDA_SIMM_CONFIG"
DEFAULT_CONFIG_PATH = "config.json"


def load_defaults() -> Dict[str, Any]:
    """Load default configuration values for the API."""
    config_path = os.getenv(CONFIG_ENV_VAR, DEFAULT_CONFIG_PATH)
    defaults: Dict[str, Any] = {
        "crif_path": "CRIF/crif.csv",
        "calculation_currency": "USD",
        "exchange_rate": 1.0,
    }

    if not os.path.exists(config_path):
        return defaults

    with open(config_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    defaults.update(config.get("defaults", {}))
    return defaults


def load_crif_dataframe(records: Optional[List[Dict[str, Any]]], crif_path: str) -> pd.DataFrame:
    """Load a CRIF dataframe from JSON records or a file path."""
    if records is not None:
        if len(records) == 0:
            raise HTTPException(status_code=400, detail="JSON payload must include at least one record.")
        return pd.DataFrame(records)

    if not os.path.exists(crif_path):
        raise HTTPException(status_code=400, detail=f"CRIF file not found at {crif_path}.")

    return pd.read_csv(crif_path, header=0)


class SimmRequest(BaseModel):
    """Request payload for SIMM calculations."""

    records: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="CRIF rows as JSON objects. When omitted, the server reads the default CRIF file.",
    )
    calculation_currency: Optional[str] = Field(
        default=None,
        description="Calculation currency override (defaults from config.json).",
    )
    exchange_rate: Optional[float] = Field(
        default=None,
        description="Exchange rate override (defaults from config.json).",
    )
    return_breakdown: bool = Field(
        default=True,
        description="Include SIMM breakdown details in the response.",
    )


app = FastAPI(
    title="ISDA SIMM API",
    description="REST API for computing ISDA SIMM initial margin values.",
    version="1.0.0",
)


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Simple health check for the API."""
    return {"status": "ok"}


@app.post("/simm")
def calculate_simm(payload: SimmRequest) -> Dict[str, Any]:
    """Calculate SIMM totals and return results as JSON."""
    defaults = load_defaults()

    calc_currency = payload.calculation_currency or defaults["calculation_currency"]
    rate = payload.exchange_rate if payload.exchange_rate is not None else defaults["exchange_rate"]
    path = defaults["crif_path"]

    crif = load_crif_dataframe(payload.records, path)
    portfolio = SIMM(crif, calc_currency, rate)

    response: Dict[str, Any] = {
        "simm_total": portfolio.simm,
        "calculation_currency": calc_currency,
        "exchange_rate": rate,
    }

    if payload.return_breakdown:
        response["breakdown"] = portfolio.simm_break_down.reset_index().to_dict(orient="records")

    return response
