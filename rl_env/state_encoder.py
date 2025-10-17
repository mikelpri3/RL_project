from dataclasses import dataclass
from typing import Dict

def hp_to_bucket(hp_actual: float, hp_total: float, n_buckets: int = 5) -> int:
    if hp_actual <= 0:
        return 0
    width = max(1, int(hp_total // n_buckets))
    b = int((hp_actual - 1) // width) + 1
    return min(b, n_buckets)

@dataclass(frozen=True)
class TinyState:
    our_hp_b: int
    opp_hp_b: int
    matchup: int
    ours_left: int    # 1..3
    opps_left: int    # 1..3

class StateEncoder:
    """
    Dictionary that maps the TinyState to an int, so the agent see a number 
    which represents a unique combination of our_hp_bucket, opp_hp_bucket, matchup, ours_left, opps_left
    """
    def __init__(self): 
        self._to_id: Dict[TinyState,int] = {}
        self._from_id: Dict[int,TinyState] = {}
    def encode(self, s: TinyState) -> int:
        if s in self._to_id: return self._to_id[s]
        i = len(self._to_id)
        self._to_id[s] = i; self._from_id[i] = s
        return i
