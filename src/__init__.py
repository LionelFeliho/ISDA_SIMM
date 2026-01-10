"""Shared constants for SIMM calculations."""

from __future__ import annotations

from typing import Dict, List

list_vega: List[str] = [
    'Risk_IRVol',
    'Risk_InflationVol',
    'Risk_CreditVol',
    'Risk_CreditVolNonQ',
    'Risk_EquityVol',
    'Risk_CommodityVol',
    'Risk_FXVol',
]
full_bucket_list: List[str] = [
    '1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','Residual',
]
simm_tenor_list: List[str] = ['2w','1m','3m','6m','1y','2y','3y','5y','10y','15y','20y','30y']
list_rates: List[str] = ['Risk_IRCurve', 'Risk_Inflation', 'Risk_XCcyBasis', 'Risk_IRVol', 'Risk_InflationVol']
list_fx: List[str] = ['Risk_FX', 'Risk_FXVol']
list_creditQ: List[str] = ['Risk_CreditQ', 'Risk_CreditVol', 'Risk_BaseCorr']
list_credit_nonQ: List[str] = ['Risk_CreditNonQ', 'Risk_CreditVolNonQ']
list_equity: List[str] = ['Risk_Equity', 'Risk_EquityVol']
list_commodity: List[str] = ['Risk_Commodity', 'Risk_CommodityVol']

dict_margin_by_risk_class: Dict[str, Dict[str, float]] = {

    'Rates':     {'Delta'      :0, \
                  'Vega'       :0, \
                  'Curvature'  :0, \
                  'BaseCorr'   :0},\

    'FX':        {'Delta'      :0, \
                  'Vega'       :0, \
                  'Curvature'  :0, \
                  'BaseCorr'   :0},\

    'CreditQ':   {'Delta'      :0, \
                  'Vega'       :0, \
                  'Curvature'  :0, \
                  'BaseCorr'   :0},\

    'CreditNonQ':{'Delta'      :0, \
                  'Vega'       :0, \
                  'Curvature'  :0, \
                  'BaseCorr'   :0},\

    'Equity':    {'Delta'      :0, \
                  'Vega'       :0, \
                  'Curvature'  :0, \
                  'BaseCorr'   :0},\

    'Commodity': {'Delta'      :0, \
                  'Vega'       :0, \
                  'Curvature'  :0, \
                  'BaseCorr'   :0}
                  
}
