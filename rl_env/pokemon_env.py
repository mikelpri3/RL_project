# rl_env/pokemon_env.py
from typing import Dict, Optional
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from data import crear_todos_los_entrenadores
from combate import Combate

from rl_env.state_encoder import hp_to_bucket, TinyState, StateEncoder
from rl_env.utils_types import _m, coarse_matchup


class PokemonEnv(gym.Env):
    """
    Gymnasium-compliant wrapper over our Combate engine.
    Actions:
      - 0..3: usar movimiento i (si existe)
      - 10+idx_equipo: cambiar al pokémon del slot idx (si está vivo y no es el activo)
    Observation:
      - single integer id encoding (our_hp_bucket, opp_hp_bucket, coarse matchup, ours_left, opps_left)
    """
    metadata = {"render_modes": []}

    def __init__(self, n_buckets: int = 5, max_steps: int = 200, seed: Optional[int] = None):
        super().__init__()
        self.n_buckets = n_buckets
        self.max_steps = max_steps
        self.encoder = StateEncoder()
        self.rng = np.random.default_rng(seed)
        self._t = 0

        # Build trainers and a factory to make fresh Combate each reset
        entrenadores = crear_todos_los_entrenadores()
        self.t1 = entrenadores[1]  # agente
        self.t2 = entrenadores[2]  # bot
        self.battle: Optional[Combate] = None

        # Spaces (upper bounds; legality via action_mask)
        # We allow up to 16 discrete actions (4 moves + up to 12 switches is plenty)
        self.action_space = spaces.Discrete(16)
        # Observation is an integer index; we set a generous bound
        self.observation_space = spaces.Discrete(200_000)

    # --- required Gym API ---
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self._t = 0
        self.battle = Combate(self.t1, self.t2)  # our engine
        obs = self._obs_from_raw(self.battle.estado_raw())
        info = {"action_mask": self._action_mask()}
        return obs, info

    def step(self, action: int):
        assert self.battle is not None, "Call reset() before step()."
        self._t += 1

        # Mask illegal actions (fallback to first legal)
        mask = self._action_mask()
        if action < 0 or action >= len(mask) or not mask[action]:
            # Pick first legal action deterministically (or random among legals)
            legal_idxs = np.flatnonzero(mask)
            action = int(legal_idxs[0])

        reward, ended = self.battle.step_rl(action)
        terminated = bool(ended)
        truncated = (self._t >= self.max_steps) and not terminated

        obs = self._obs_from_raw(self.battle.estado_raw())
        info = {"action_mask": self._action_mask()}

        return obs, float(reward), terminated, truncated, info

    # --- helpers ---
    def _obs_from_raw(self, s: Dict) -> int:
        our_b = hp_to_bucket(s["our_hp_actual"], s["our_hp_total"], self.n_buckets)
        opp_b = hp_to_bucket(s["opp_hp_actual"], s["opp_hp_total"], self.n_buckets)
        matchup = coarse_matchup(s["our_type1"], s["our_type2"], s["opp_type1"], s["opp_type2"])
        tiny = TinyState(
            our_hp_b=our_b,
            opp_hp_b=opp_b,
            matchup=matchup,
            ours_left=int(s["our_team_left"]),
            opps_left=int(s["opp_team_left"]),
        )
        return self.encoder.encode(tiny)

    def _action_mask(self) -> np.ndarray:
        # Mark legal indices True
        legales = self.battle.acciones_legales_agente()
        mask = np.zeros(self.action_space.n, dtype=bool)
        if len(legales) > 0:
            mask[np.array(legales, dtype=int)] = True
        return mask
