import argparse, numpy as np
from rl_env.pokemon_env import PokemonEnv
from rl_agents.tabular_q import TabularQLearner
from utils.checkpoint import load_checkpoint

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", type=str, required=True)
    ap.add_argument("--episodes", type=int, default=200)
    args = ap.parse_args()

    env = PokemonEnv(max_steps=200)
    agent = TabularQLearner(n_actions=env.action_space.n)
    load_checkpoint(agent, env, args.ckpt)
    print(f"[load] {args.ckpt} (rows={len(agent.Q)})")

    rng = np.random.default_rng(123)
    wins, rets = 0, []
    for _ in range(args.episodes):
        obs, info = env.reset(seed=int(rng.integers(1_000_000)))
        term = trunc = False
        G = 0.0
        while not (term or trunc):
            legal = np.flatnonzero(info["action_mask"])
            q = agent.Q[obs]
            a = int(legal[np.argmax(q[legal])]) if len(legal) else 0
            obs, r, term, trunc, info = env.step(a)
            G += r
        rets.append(G)
        if term and G > 0:
            wins += 1
    print(f"Greedy win-rate: {wins/args.episodes:.3f} | avg return: {np.mean(rets):.3f}")

if __name__ == "__main__":
    main()
