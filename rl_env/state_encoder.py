from dataclasses import dataclass
from typing import Dict

def hp_to_bucket(hp, hp_max, n_buckets=5):
    if hp <= 0: return 0
    w = max(1, hp_max // n_buckets)
    b = (hp - 1)//w + 1
    return min(b, n_buckets)

@dataclass(frozen=True)
class TinyState:
    our_hp_b: int
    opp_hp_b: int
    matchup: int

class StateEncoder:
    def __init__(self): 
        self._to_id: Dict[TinyState,int] = {}
        self._from_id: Dict[int,TinyState] = {}
    def encode(self, s: TinyState) -> int:
        if s in self._to_id: return self._to_id[s]
        i = len(self._to_id)
        self._to_id[s] = i; self._from_id[i] = s
        return i
