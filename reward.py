# reward.py
from typing import Optional
from types import SimpleNamespace
from danio import calcular_efectividad
import math

"""
We're trying to design a reward function that encourages the agent to win battles
efficiently while also promoting good battle strategies. The reward function combines
various components to provide feedback at each turn as well as at the end of the battle.
We give a large bonus for winning and a large penalty for losing, along with smaller shaping rewards
based on damage dealt/received, effectiveness of moves, and strategic switches (only if improves expected matchup).
Also a small per-step penalty to discourage stalling.
The weights for each component can be tuned to adjust the agent's behavior.
Additionally use percentages wrt max HP, not current HP, because dividing by current HP 
can lead to huge spikes in reward when a Pokémon is low on health.

"""
# ----------------- tunable weights (start here) -----------------
KILL_BONUS       = 30.0   # per KO done this turn (non-terminal)
DEATH_PENALTY    = 30.0   # per KO suffered this turn (non-terminal)
WIN_BONUS        = 100.0  # battle victory (terminal)
LOSE_PENALTY     = 100.0  # battle defeat (terminal)

W_DMG            = 1.0    # weight for net % damage (you - opp)
W_EFF            = 0.25   # weight for effectiveness ratio shaping
W_SWITCH_BENEFIT = 0.50   # reward for switching to better expected matchup
STEP_PENALTY     = 0.01   # small per-step negative to discourage stalling
CLIP_PER_STEP    = 2.0    # clip shaping to ±2 before adding big terminal bonuses
# ----------------------------------------------------------------

def _ensure_hp_max(poke) -> float:
    """
    Cache a per-Pokémon max HP on first sight.
    We store it as an attribute so we don't need schema changes.
    """
    if poke is None:
        return 1.0
    if not hasattr(poke, "_hp_max"):
        # first time we see this Pokémon in the battle, assume current hp is max
        # (your engine should set hp at reset/start)
        setattr(poke, "_hp_max", float(max(1, getattr(poke, "hp", 1))))
    return float(getattr(poke, "_hp_max"))

def _eff_mult(att_type: Optional[str], def_t1: Optional[str], def_t2: Optional[str]) -> float:
    """Multiplicative offensive effectiveness with safe defaults."""
    def e(att, d):
        if att is None or d is None:
            return 1.0
        return float(calcular_efectividad(att, d))
    if att_type is None:
        return 1.0
    return e(att_type, def_t1) * e(att_type, def_t2)

def _best_offensive_eff(attacker, defender) -> float:
    """Best available offensive effectiveness among attacker's moves."""
    if attacker is None or not getattr(attacker, "movimientos", None):
        return 1.0
    best = 1.0
    for mov in attacker.movimientos:
        best = max(best, _eff_mult(mov.type, defender.type1, defender.type2))
    return best

def _current_move_eff(move, defender) -> float:
    if move is None:
        return 1.0
    return _eff_mult(move.type, defender.type1, defender.type2)

def calcular_reward_turno(
    danio_hecho: float,
    danio_recibido: float,
    pokemon_jugador,            # our active AFTER resolution
    pokemon_oponente,           # opponent active AFTER resolution
    movimiento_jugador,         # real move OR SimpleNamespace(name="Cambio")
    movimiento_oponente,        # may be None -> treated as neutral
    oponente_pre_cambio=None,   # opponent that started the turn (if it switched)
    vida_oponente_antes_ko: Optional[float] = None,  # opp HP just before KO (if KO)
    vida_jugador_antes_ko: Optional[float] = None,   # our HP just before KO (if KO)
    done: bool = False,         # battle ended this step?
    agent_won: Optional[bool] = None,  # who won (if done)?
) -> float:
    """
    Dense per-step shaping (clipped) + strong terminal signal (win/lose).
    Assumes your engine normalizes movimiento_jugador to have .name ("Cambio" if switch).
    """
    # Which defender to evaluate against (if they switched this turn)?
    opp_eval = oponente_pre_cambio if oponente_pre_cambio is not None else pokemon_oponente

    # --- percentage damage wrt MAX hp (stable shaping) ---
    opp_max = _ensure_hp_max(opp_eval)
    our_max = _ensure_hp_max(pokemon_jugador)

    pct_dmg_dealt    = float(danio_hecho)    / max(1.0, opp_max)
    pct_dmg_received = float(danio_recibido) / max(1.0, our_max)

    # --- KO shaping (non-terminal) ---
    ko_term = 0.0
    if vida_oponente_antes_ko is not None:
        ko_term += KILL_BONUS
    if vida_jugador_antes_ko is not None:
        ko_term -= DEATH_PENALTY

    # --- effectiveness shaping ---
    # if we switched, reward only if the NEW active has a better offensive matchup than neutral
    if getattr(movimiento_jugador, "name", "") == "Cambio":
        # reward proportional to how much better than neutral (1.0) our best move could be now
        best_eff = _best_offensive_eff(pokemon_jugador, opp_eval)
        switch_gain = max(0.0, best_eff - 1.0)
        eff_term = W_SWITCH_BENEFIT * switch_gain
    else:
        # offensive vs defensive effectiveness ratio (centered at 0 by subtracting 1.0)
        off_eff = _current_move_eff(movimiento_jugador, opp_eval)
        # defensive: opponent's move into us (if None, treat neutral)
        def_eff = _current_move_eff(movimiento_oponente, pokemon_jugador) if movimiento_oponente else 1.0
        if def_eff <= 0:
            def_eff = 0.01
        eff_ratio = off_eff / def_eff
        eff_term  = W_EFF * (eff_ratio - 1.0)

    # --- net damage shaping + tiny time penalty ---
    dmg_term  = W_DMG * (pct_dmg_dealt - pct_dmg_received)
    step_term = -STEP_PENALTY

    shaping = dmg_term + eff_term + ko_term + step_term
    # keep per-step shaping bounded so terminal rewards dominate
    shaping = max(-CLIP_PER_STEP, min(CLIP_PER_STEP, shaping))

    # --- terminal dominance ---
    terminal = 0.0
    if done and agent_won is not None:
        terminal = WIN_BONUS if agent_won else -LOSE_PENALTY

    return shaping + terminal