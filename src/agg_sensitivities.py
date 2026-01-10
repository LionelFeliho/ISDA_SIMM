from __future__ import annotations

import logging
import math
from typing import Iterable, List, Optional

import numpy as np

from . import wnc
from . import (
    list_creditQ,
    list_credit_nonQ,
    list_equity,
    list_commodity,
    list_fx,
)

LOGGER = logging.getLogger(__name__)


def k_delta(
    risk_class: str,
    list_WS: Iterable[float],
    list_CR: Optional[Iterable[float]] = None,
    bucket: Optional[Iterable[str]] = None,
    tenor: Optional[Iterable[str]] = None,
    index: Optional[Iterable[str]] = None,
    calculation_currency: str = 'USD',
) -> float:
    """Aggregate weighted sensitivities for delta margin."""

    list_ws = list(list_WS)
    list_cr = list(list_CR) if list_CR is not None else []
    list_bucket = list(bucket) if isinstance(bucket, (list, tuple)) else []
    bucket_value = bucket if not isinstance(bucket, (list, tuple)) else None
    list_tenor = list(tenor) if tenor is not None else []
    list_index = list(index) if index is not None else []

    K = sum([np.array([WS], dtype='double')[0]**2 for WS in list_ws]) # numpy is used due to overflow issue
    for i, _ in enumerate(list_ws):
        for j, _ in enumerate(list_ws):
            if i == j:
                continue
            else:    
                # Rates
                if risk_class == 'Rates':

                    if (list_index[i] == list_index[j]):
                        phi = 1
                    
                    elif (list_index[i] == 'XCcy') or (list_index[j] == 'XCcy'):
                        phi = wnc.ccy_basis_spread_corr

                    elif (list_index[i] == 'Inf') or (list_index[j] == 'Inf'):
                        phi = wnc.inflation_corr

                    else:
                        phi = wnc.sub_curves_corr

                    if (list_index[i] not in ['Inf','XCcy']) and (list_index[j] not in ['Inf','XCcy']):
                        rho = wnc.rho('Risk_IRCurve', list_tenor[i], list_tenor[j])

                    else:
                        rho = 1                   
                
                # Credit
                elif risk_class in list_creditQ + list_credit_nonQ:
                    rho = wnc.rho(risk_class, list_index[i], list_index[j])
                    
                # Equity, Commodity, FX
                else:
                    if risk_class in list_equity + list_commodity:
                        rho = wnc.rho(risk_class, bucket=bucket_value)

                    elif risk_class in list_fx:
                                        
                        currency1 = list_bucket[i]
                        currency2 = list_bucket[j]

                        is_ccy1_high_vol = currency1 in wnc.high_vol_currency_group
                        is_ccy2_high_vol = currency2 in wnc.high_vol_currency_group

                        if calculation_currency not in wnc.high_vol_currency_group:
                            if (is_ccy1_high_vol==True) and (is_ccy2_high_vol==True):
                                rho = wnc.fx_reg_vol_corr['High']['High']
                            elif (is_ccy1_high_vol==True) and (is_ccy2_high_vol==False):
                                rho = wnc.fx_reg_vol_corr['High']['Regular']
                            elif (is_ccy1_high_vol==False) and (is_ccy2_high_vol==True):
                                rho = wnc.fx_reg_vol_corr['Regular']['High']
                            else:
                                rho = wnc.fx_reg_vol_corr['Regular']['Regular']
                        else:
                            if (is_ccy1_high_vol==True) and (is_ccy2_high_vol==True):
                                rho = wnc.fx_high_vol_corr['High']['High']
                            elif (is_ccy1_high_vol==True) and (is_ccy2_high_vol==False):
                                rho = wnc.fx_high_vol_corr['High']['Regular']
                            elif (is_ccy1_high_vol==False) and (is_ccy2_high_vol==True):
                                rho = wnc.fx_high_vol_corr['Regular']['High']
                            else:
                                rho = wnc.fx_high_vol_corr['Regular']['Regular']
                    
                if risk_class == 'Rates':
                    f = 1
                
                else:
                    f = min(list_cr[i], list_cr[j]) / max(list_cr[i], list_cr[j])
                    phi = 1

                K += rho * list_ws[i] * list_ws[j] * phi * f
    
    LOGGER.debug("Computed k_delta for %s: %s", risk_class, K)
    return math.sqrt(K)
    

def k_vega(
    risk_class: str,
    VR: Iterable[float],
    VCR: Optional[Iterable[float]] = None,
    bucket: Optional[str] = None,
    index: Iterable[str] | str = '',
) -> float:
    """Aggregate vega sensitivities."""

    list_vr = list(VR)
    list_vcr = list(VCR) if VCR is not None else []
    if index == '': # duplicate '' for the iteration
        list_index = [''] * len(list_vr)
    else:
        list_index = list(index)

    K = sum([vr**2 for vr in list_vr])
    for k, (VR_k, index_k) in enumerate(zip(list_vr, list_index)):
        for l, (VR_l, index_l) in enumerate(zip(list_vr, list_index)):
            if k == l:
                continue

            else:
                if risk_class == 'Rates':
                    
                    if (index_k == 'Inf') and (index_l == 'Inf'):
                        rho = 1

                    elif (index_k == 'Inf') or (index_l == 'Inf'):
                        rho = wnc.inflation_corr

                    else:
                        rho = wnc.rho('Risk_IRVol', index_k, index_l)

                elif risk_class in list_equity + list_commodity:
                    rho = wnc.rho(risk_class,bucket=bucket)

                elif risk_class in list_fx:
                    rho = wnc.fx_vega_corr

                elif risk_class in ['Risk_CreditVol', 'Risk_CreditVolNonQ']:
                    rho = wnc.rho(risk_class, index_k, index_l)
                    
                if risk_class == 'Rates':
                    f = 1
                else:
                    f = min(list_vcr[k], list_vcr[l]) / max(list_vcr[k], list_vcr[l])
                
                K += f * rho * VR_k * VR_l

    LOGGER.debug("Computed k_vega for %s: %s", risk_class, K)
    return math.sqrt(K)


def k_curvature(
    risk_class: str,
    CVR_list: Iterable[float],
    bucket: Optional[str] = None,
    index: Optional[Iterable[str]] = None,
) -> float:
    """Aggregate curvature sensitivities."""

    list_cvr = list(CVR_list)
    list_index = list(index) if index is not None else []

    K = sum([CVR**2 for CVR in list_cvr])
    for k, _ in enumerate(list_cvr):
        for l, _ in enumerate(list_cvr):

            if k == l:
                continue

            else:
                if risk_class == 'Rates':

                    if (list_index[k] == 'Inf') and (list_index[l] == 'Inf'):
                        rho = 1

                    elif (list_index[k] == 'Inf') or (list_index[l] == 'Inf'):
                        rho = wnc.inflation_corr

                    else:
                        rho = wnc.rho('Risk_IRVol', list_index[k], list_index[l])

                        
                elif risk_class in list_equity + list_commodity:
                    rho = wnc.rho(risk_class,bucket=bucket)
                    
                elif risk_class in list_fx:
                    rho = wnc.fx_vega_corr


                elif risk_class in ['Risk_CreditVol', 'Risk_CreditVolNonQ']:

                    rho = wnc.rho(risk_class, list_index[k], list_index[l])

                K += (rho**2) * list_cvr[k] * list_cvr[l]

    LOGGER.debug("Computed k_curvature for %s: %s", risk_class, K)
    return math.sqrt(K)
