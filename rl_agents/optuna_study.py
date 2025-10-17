# rl_agents/optuna_study.py
import optuna, numpy as np
from functools import partial
from rl_env.pokemon_env import PokemonEnv
from rl_agents.tabular_q import TabularQLearner

def evaluate_greedy(env, agent, episodes=50, seed=123):
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(episodes):
        obs, info = env.reset(seed=int(rng.integers(1_000_000)))
        term = trunc = False
        while not (term or trunc):
            legal = np.flatnonzero(info["action_mask"])
            q = agent.Q[obs]
            a = int(max(legal, key=lambda i: q[i] if i < len(q) else -1e9))
            obs, r, term, trunc, info = env.step(a)
        if term and r > 0:
            wins += 1
    return wins / episodes

def train_once(alpha, gamma, eps0, eps_end, eps_decay, train_episodes=600, eval_every=200):
    env = PokemonEnv(max_steps=200)
    agent = TabularQLearner(
        n_actions=env.action_space.n,
        alpha=alpha, gamma=gamma,
        eps_start=eps0, eps_end=eps_end, eps_decay=eps_decay
    )
    # simple budget; you can add early-stopping if degenerates
    for ep in range(train_episodes):
        obs, info = env.reset()
        term = trunc = False
        while not (term or trunc):
            legal = np.flatnonzero(info["action_mask"])
            a = agent.act(obs, legal)
            obs2, r, term, trunc, info = env.step(a)
            agent.update(obs, a, r, obs2, term or trunc)
            obs = obs2
    # Greedy evaluation
    return evaluate_greedy(env, agent, episodes=100)

def objective(trial):
    alpha     = trial.suggest_float("alpha",     0.05, 0.6, log=True)
    gamma     = trial.suggest_float("gamma",     0.90, 0.999)
    eps0      = trial.suggest_float("eps0",      0.3,  1.0)
    eps_end   = trial.suggest_float("eps_end",   0.01, 0.2)
    eps_decay = trial.suggest_int(  "eps_decay", 1000, 10000)

    # Optionally average across a few seeds to reduce luck
    seeds = [11, 29, 97]
    scores = []
    for sd in seeds:
        np.random.seed(sd)
        score = train_once(alpha, gamma, eps0, eps_end, eps_decay,
                           train_episodes=600)
        scores.append(score)
        # report intermediate results for pruning
        trial.report(np.mean(scores), step=len(scores))
        if trial.should_prune():
            raise optuna.exceptions.TrialPruned()

    return float(np.mean(scores))

if __name__ == "__main__":
    pruner  = optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=1)
    sampler = optuna.samplers.TPESampler(seed=42)
    # storage = "sqlite:///optuna_pokemon.db"
    # study = optuna.create_study(direction="maximize", sampler=sampler, pruner=pruner, storage=storage, study_name="qlearn", load_if_exists=True)
    study = optuna.create_study(direction="maximize", sampler=sampler, pruner=pruner)
    study.optimize(objective, n_trials=40, n_jobs=1, show_progress_bar=True)
    print("Best:", study.best_params, "Value:", study.best_value)
