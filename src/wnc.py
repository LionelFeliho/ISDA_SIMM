"""Weights and correlations helpers."""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from Weights_and_Corr.v2_7 import *
from . import (
    list_creditQ,
    list_credit_nonQ,
    list_equity,
    list_commodity,
    list_rates,
    list_fx,
    simm_tenor_list,
)

logger = logging.getLogger(__name__)


def RW(risk_class: str, bucket: int) -> float:
    """Return risk weight for a risk class and bucket."""
    if risk_class in list_creditQ:
        return creditQ_rw[bucket]

    if risk_class in list_credit_nonQ:
        return creiditNonQ_rw[bucket]

    if risk_class in list_equity:
        return equity_rw[bucket]

    if risk_class in list_commodity:
        return commodity_rw[bucket]

    raise ValueError(f"Unknown risk class for RW: {risk_class}")


def rho(
    risk_class: str,
    index1: str | None = None,
    index2: str | None = None,
    bucket: int | None = None,
) -> float:
    """Return correlation value for a risk class."""
    if risk_class in list_rates:
        return pd.DataFrame(ir_corr, columns=simm_tenor_list, index=simm_tenor_list)[index1][
            index2
        ]

    if risk_class in list_creditQ:
        if risk_class == "Risk_BaseCorr":
            return float(creditQ_corr[3])

        if (index1 == "Res") or (index2 == "Res"):
            rho_value = creditQ_corr[2]
        elif index1 == index2:
            rho_value = creditQ_corr[0]
        else:
            rho_value = creditQ_corr[1]
        return float(rho_value)

    if risk_class in list_credit_nonQ:
        if (index1 == "Res") or (index2 == "Res"):
            rho_value = creditNonQ_corr[2]
        elif index1 == index2:
            rho_value = creditNonQ_corr[0]
        else:
            rho_value = creditNonQ_corr[1]
        return float(rho_value)

    if risk_class in list_equity:
        return equity_corr[bucket]

    if risk_class in list_commodity:
        return commodity_corr[bucket]

    raise ValueError(f"Unknown risk class for rho: {risk_class}")


def gamma(risk_class: str, bucket1: str | None = None, bucket2: str | None = None) -> float:
    """Return gamma correlations for a risk class."""
    if risk_class in list_creditQ:
        bucket_list = [str(i) for i in range(1, 13)]
        return pd.DataFrame(
            creditQ_corr_non_res, columns=bucket_list, index=bucket_list
        )[bucket1][bucket2]

    if risk_class in list_credit_nonQ:
        return cr_gamma_diff_ccy

    if risk_class in list_equity:
        bucket_list = [str(i) for i in range(1, 13)]
        return pd.DataFrame(
            equity_corr_non_res, columns=bucket_list, index=bucket_list
        )[bucket1][bucket2]

    if risk_class in list_commodity:
        bucket_list = [str(i) for i in range(1, 18)]
        return pd.DataFrame(
            commodity_corr_non_res, columns=bucket_list, index=bucket_list
        )[bucket1][bucket2]

    raise ValueError(f"Unknown risk class for gamma: {risk_class}")


def T(
    risk_class: str,
    type: str,
    currency: str | None = None,
    bucket: int | None = None,
) -> float:
    """Return concentration threshold for risk class/type."""
    if type == "Delta":
        if risk_class == "Rates":
            try:
                threshold = ir_delta_CT[currency]
            except KeyError:
                threshold = ir_delta_CT["Others"]

        elif risk_class in list_creditQ:
            threshold = credit_delta_CT["Qualifying"][bucket]

        elif risk_class in list_credit_nonQ:
            threshold = credit_delta_CT["Non-Qualifying"][bucket]

        elif risk_class in list_equity:
            threshold = equity_delta_CT[bucket]

        elif risk_class in list_commodity:
            threshold = commodity_delta_CT[bucket]

        elif risk_class in list_fx:
            if currency in fx_category1:
                threshold = fx_delta_CT["Category1"]
            elif currency in fx_category2:
                threshold = fx_delta_CT["Category2"]
            else:
                threshold = fx_delta_CT["Others"]

    elif type == "Vega":
        if risk_class == "Rates":
            try:
                threshold = ir_vega_CT[currency]
            except KeyError:
                threshold = ir_vega_CT["Others"]

        elif risk_class in list_creditQ:
            threshold = credit_vega_CT["Qualifying"]

        elif risk_class in list_credit_nonQ:
            threshold = credit_vega_CT["Non-Qualifying"]

        elif risk_class in list_equity:
            threshold = equity_vega_CT[bucket]

        elif risk_class in list_commodity:
            threshold = commodity_vega_CT[bucket]

        elif risk_class in list_fx:
            currency1 = currency[0:3]
            currency2 = currency[3:6]

            if (currency1 in fx_category1) and (currency2 in fx_category1):
                threshold = fx_vega_CT["Category1-Category1"]

            elif ((currency1 in fx_category1) and (currency2 in fx_category2)) or (
                (currency1 in fx_category2) and (currency2 in fx_category1)
            ):
                threshold = fx_vega_CT["Category1-Category2"]

            elif ((currency1 in fx_category1) and (currency2 not in fx_category1 + fx_category2)) or (
                (currency1 not in fx_category1 + fx_category2) and (currency2 in fx_category1)
            ):
                threshold = fx_vega_CT["Category1-Category3"]

            elif (currency1 in fx_category2) and (currency2 in fx_category2):
                threshold = fx_vega_CT["Category2-Category2"]

            elif ((currency1 in fx_category2) and (currency2 not in fx_category1 + fx_category2)) or (
                (currency1 not in fx_category1 + fx_category2) and (currency2 in fx_category2)
            ):
                threshold = fx_vega_CT["Category2-Category3"]

            elif (currency1 not in fx_category1 + fx_category2) and (
                currency2 not in fx_category1 + fx_category2
            ):
                threshold = fx_vega_CT["Category3-Category3"]

    return threshold * 1000000


def psi(risk_class1: str, risk_class2: str) -> float:
    """Return risk class correlation parameter."""
    return pd.DataFrame(
        corr_params,
        columns=["Rates", "CreditQ", "CreditNonQ", "Equity", "Commodity", "FX"],
        index=["Rates", "CreditQ", "CreditNonQ", "Equity", "Commodity", "FX"],
    )[risk_class1][risk_class2]
