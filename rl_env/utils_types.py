from data import datos_efectividad, TIPOS  # TIPOS list from data.py

TIPO2IDX = {t: i for i, t in enumerate(TIPOS)}

def type_multiplier(attacker: str, defender: str) -> float:
    i, j = TIPO2IDX[attacker], TIPO2IDX[defender]
    return float(datos_efectividad[i][j])

def coarse_matchup(attacker: str, defender: str) -> int:
    m = type_multiplier(attacker, defender)
    if m == 0: return -1
    if m > 1.01: return +1
    elif m < 0.99: return -1
    return 0
