# rl_agents/optuna_study.py
import argparse, os, optuna, numpy as np
from rl_env.pokemon_env import PokemonEnv
from rl_agents.tabular_q import TabularQLearner
from utils.checkpoint import save_checkpoint

def evaluate_greedy(env, agent, episodes=50, seed=123):
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(episodes):
        obs, info = env.reset(seed=int(rng.integers(1_000_000)))
        term = trunc = False
        while not (term or trunc):
            legal = np.flatnonzero(info["action_mask"])
            q = agent.Q[obs]
            a = int(legal[np.argmax(q[legal])]) if len(legal) else 0
            obs, r, term, trunc, info = env.step(a)
        if term and r > 0:
            wins += 1
    return wins / episodes

def train_once(alpha, gamma, eps0, eps_end, eps_decay, train_episodes=600, max_steps=200, seed=0):
    env = PokemonEnv(max_steps=max_steps)
    agent = TabularQLearner(n_actions=env.action_space.n,
                            alpha=alpha, gamma=gamma,
                            eps_start=eps0, eps_end=eps_end, eps_decay=eps_decay)
    rng = np.random.default_rng(seed)
    for _ in range(train_episodes):
        obs, info = env.reset(seed=int(rng.integers(1_000_000)))
        term = trunc = False
        while not (term or trunc):
            legal = np.flatnonzero(info["action_mask"])
            a = agent.act(obs, legal)
            obs2, r, term, trunc, info = env.step(a)
            agent.update(obs, a, r, obs2, term or trunc)
            obs = obs2
    return evaluate_greedy(env, agent, episodes=100, seed=seed+999)

def objective(train_episodes):
    def _objective(trial):
        alpha     = trial.suggest_float("alpha",     0.05, 0.6, log=True)
        gamma     = trial.suggest_float("gamma",     0.90, 0.999)
        eps0      = trial.suggest_float("eps0",      0.3,  1.0)
        eps_end   = trial.suggest_float("eps_end",   0.01, 0.2)
        eps_decay = trial.suggest_int(  "eps_decay", 1000, 10000)

        seeds = [11, 29, 97]
        scores = []
        for i, sd in enumerate(seeds, 1):
            score = train_once(alpha, gamma, eps0, eps_end, eps_decay,
                               train_episodes=train_episodes, seed=sd)
            scores.append(score)
            trial.report(float(np.mean(scores)), step=i)
            if trial.should_prune():
                raise optuna.exceptions.TrialPruned()
        return float(np.mean(scores))
    return _objective

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=40)
    ap.add_argument("--train-episodes", type=int, default=600)
    ap.add_argument("--final-train-episodes", type=int, default=800)
    args = ap.parse_args()

    pruner  = optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=1)
    sampler = optuna.samplers.TPESampler(seed=42)
    study = optuna.create_study(direction="maximize", sampler=sampler, pruner=pruner)
    study.optimize(objective(args.train_episodes), n_trials=args.trials, n_jobs=1, show_progress_bar=True)

    print("Best value:", study.best_value)
    print("Best params:", study.best_params)

    # Retrain ONCE with best params and save
    best = study.best_params
    env  = PokemonEnv(max_steps=200)
    agent = TabularQLearner(n_actions=env.action_space.n,
                            alpha=best["alpha"], gamma=best["gamma"],
                            eps_start=best["eps0"], eps_end=best["eps_end"], eps_decay=best["eps_decay"])
    for _ in range(args.final_train_episodes):
        obs, info = env.reset()
        term = trunc = False
        while not (term or trunc):
            legal = np.flatnonzero(info["action_mask"])
            a = agent.act(obs, legal)
            obs2, r, term, trunc, info = env.step(a)
            agent.update(obs, a, r, obs2, term or trunc)
            obs = obs2

    os.makedirs("checkpoints", exist_ok=True)
    save_checkpoint(agent, env, "checkpoints/best_q.pkl")
    print("Saved best checkpoint to checkpoints/best_q.pkl")

if __name__ == "__main__":
    main()
