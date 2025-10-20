import numpy as np
from rl_env.pokemon_env import PokemonEnv

def main():
    env = PokemonEnv(max_steps=50)
    obs, info = env.reset(seed=123)
    term = trunc = False
    steps = 0
    while not (term or trunc):
        legal = np.flatnonzero(info["action_mask"])
        a = int(np.random.choice(legal)) if len(legal) else 0
        obs, r, term, trunc, info = env.step(a)
        steps += 1
    print(f"Smoke test OK. Reached end after {steps} steps. terminated={term}, truncated={trunc}")

if __name__ == "__main__":
    main()
