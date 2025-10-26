import numpy as np
import pickle
import csv
from rl_env.pokemon_env import PokemonEnv
from rl_agents.tabular_sarsa import TabularSarsaLearner

# ---------- Greedy evaluation (ε = 0) ----------
def evaluate_greedy(env: PokemonEnv, agent: TabularSarsaLearner, episodes: int = 50, seed: int = 123):
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

    # Archivos de salida
    log_filepath = "./logs/train_log_sarsa.csv"
    q_table_filepath = "./checkpoints/sarsa_q_table.pkl"

    # ----- env & agent -----
    env = PokemonEnv(max_steps=200)
    agent = TabularSarsaLearner(
        n_actions=env.action_space.n,
        alpha=0.30,
        gamma=0.99,
        eps_start=1.0,   # start very exploratory
        eps_end=0.05,    # end mostly greedy
        eps_decay=4000   # slower decay = more early exploration
    )

    # ----- Preparación del archivo de logs -----
    log_fieldnames = ["episode", "train_return", "steps", "epsilon", "q_rows", "eval_winrate"]
    with open(log_filepath, 'w', newline='') as log_file:
        log_writer = csv.DictWriter(log_file, fieldnames=log_fieldnames)
        log_writer.writeheader()

        # ----- training loop with periodic evaluation -----
        n_episodes = 1000
        eval_every = 50

        for ep in range(1, n_episodes + 1):
            obs, info = env.reset()
            terminated = truncated = False
            G = 0.0
            steps = 0

            # SARSA CHANGE 1: Choose first action *before* the loop
            legal = np.flatnonzero(info["action_mask"])
            a = agent.act(obs, legal)

            while not (terminated or truncated):
                # SARSA CHANGE 2: Step the environment with the current action
                obs2, r, terminated, truncated, info = env.step(a)

                # SARSA CHANGE 3: Choose the *next* action a2 from the new state obs2
                # This is needed for the on-policy update.
                # If the episode is over, there is no next action.
                if terminated or truncated:
                    a2 = None
                else:
                    legal2 = np.flatnonzero(info["action_mask"])
                    a2 = agent.act(obs2, legal2)

                # SARSA CHANGE 4: Update using the (S, A, R, S', A') tuple
                agent.update(obs, a, r, obs2, a2, terminated or truncated)

                # SARSA CHANGE 5: The next state and action become the current ones
                obs = obs2
                a = a2
                
                G += r
                steps += 1

            if ep % eval_every == 0:
                wr = evaluate_greedy(env, agent, episodes=100)  # more episodes = lower variance
                print(f"ep={ep:4d}  train_return={G:6.2f}  steps={steps:3d}  greedy_winrate={wr:.2f}")

                # Escribir en el archivo CSV
                log_writer.writerow({
                    "episode": ep,
                    "train_return": round(G, 2),
                    "steps": steps,
                    "epsilon": round(agent._eps(), 4),
                    "q_rows": len(agent.Q),
                    "eval_winrate": round(wr, 2)
                })
    
    
    print(f"\nEntrenamiento completado. Guardando la tabla Q en '{q_table_filepath}'...")
    with open(q_table_filepath, 'wb') as f:
        pickle.dump(dict(agent.Q), f)

if __name__ == "__main__":
    main()