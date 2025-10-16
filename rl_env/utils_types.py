from data import df_tipos
from typing import Optional
import numpy as np


def _m(att: Optional[str], d: Optional[str]) -> float:
    """
    Return the type effectiveness multiplier for an attack type att
    hitting a deffender type d  
    """
    if att is None or (isinstance(att, float) and np.isnan(att)):
        return 1.0
    if d   is None or (isinstance(d,   float) and np.isnan(d)):
        return 1.0
    return float(df_tipos.loc[att, d])

def coarse_matchup(att1: Optional[str], att2: Optional[str],
                   def1: Optional[str], def2: Optional[str]) -> int:
    # choose the better attacking type vs defender’s two types
    """
    function to simplify the type advantage into three discrete levels so 
    the Q-table can sta small but still capture essential signal
    """
    mults = []
    for att in (att1, att2):
        if att is None or (isinstance(att, float) and np.isnan(att)):
            continue
        mults.append(_m(att, def1) * _m(att, def2))
    if not mults:
        mults = [1.0]
    M = max(mults)
    if M > 1.01: return +1
    if M < 0.99: return -1
    return 0