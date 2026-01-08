"""Top-level package for SIMM constants loaded from config.json."""
from __future__ import annotations

from .config import load_config

CONFIG = load_config()

list_vega = CONFIG["lists"]["vega"]
full_bucket_list = CONFIG["lists"]["full_bucket"]
simm_tenor_list = CONFIG["lists"]["simm_tenor"]
list_rates = CONFIG["lists"]["rates"]
list_fx = CONFIG["lists"]["fx"]
list_creditQ = CONFIG["lists"]["credit_qualifying"]
list_credit_nonQ = CONFIG["lists"]["credit_non_qualifying"]
list_equity = CONFIG["lists"]["equity"]
list_commodity = CONFIG["lists"]["commodity"]

dict_margin_by_risk_class = CONFIG["dict_margin_by_risk_class"]
