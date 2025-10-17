import numpy as np
from rl_env.pokemon_env import PokemonEnv
from rl_agents.tabular_q import TabularQLearner

# ---------- Greedy evaluation (ε = 0) ----------
def evaluate_greedy(env: PokemonEnv, agent: TabularQLearner, episodes: int = 50, seed: int = 123):
    """
    Runs episodes with a purely greedy policy (no exploration, no learning).
    Returns the win-rate in [0,1].
    """
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(episodes):
        # re-seed env for reproducibility across evals (optional)
        obs, info = env.reset(seed=int(rng.integers(1_000_000)))
        terminated = truncated = False
        while not (terminated or truncated):
            legal = np.flatnonzero(info["action_mask"])
            q = agent.Q[obs]  # shape: [n_actions]
            # greedy among legal; guard in case q shorter than action_space.n
            a = int(legal[np.argmax(q[legal])]) if len(legal) else 0
            obs, r, terminated, truncated, info = env.step(a)
        if terminated and r > 0:
            wins += 1
    return wins / episodes

def main():
    # ----- env & agent -----
    env = PokemonEnv(max_steps=200)
    agent = TabularQLearner(
        n_actions=env.action_space.n,
        alpha=0.30,
        gamma=0.99,
        eps_start=1.0,   # start very exploratory
        eps_end=0.05,    # end mostly greedy
        eps_decay=4000   # slower decay = more early exploration
    )

    # ----- training loop with periodic evaluation -----
    n_episodes = 1000
    eval_every = 50

    for ep in range(1, n_episodes + 1):
        obs, info = env.reset()
        terminated = truncated = False
        G = 0.0
        steps = 0

        while not (terminated or truncated):
            legal = np.flatnonzero(info["action_mask"])          # legal action indices now
            a = agent.act(obs, legal)                            # ε-greedy among legal
            obs2, r, terminated, truncated, info = env.step(a)  # Gymnasium 5-tuple
            agent.update(obs, a, r, obs2, terminated or truncated)
            obs = obs2
            G += r
            steps += 1

        if ep % eval_every == 0:
            wr = evaluate_greedy(env, agent, episodes=100)  # more episodes = lower variance
            print(f"ep={ep:4d}  train_return={G:6.2f}  steps={steps:3d}  greedy_winrate={wr:.2f}")

if __name__ == "__main__":
    main()
