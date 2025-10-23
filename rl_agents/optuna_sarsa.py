# rl_agents/optuna_sarsa.py
import argparse
import os
import optuna
import numpy as np
from rl_env.pokemon_env import PokemonEnv
from rl_agents.tabular_sarsa import TabularSarsaLearner
from utils.checkpoint import save_checkpoint

# Esta función no necesita cambios.
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

# --- CORRECCIÓN AQUÍ: Bucle de entrenamiento SARSA ---
def train_agent(agent, env, train_episodes, seed):
    """Entrena un agente en un entorno por un número de episodios."""
    rng = np.random.default_rng(seed)
    for _ in range(train_episodes):
        obs, info = env.reset(seed=int(rng.integers(1_000_000)))
        legal = np.flatnonzero(info["action_mask"])
        action = agent.act(obs, legal)  # Elige la primera acción 'a'

        term = trunc = False
        while not (term or trunc):
            # Realiza la acción 'a' y observa 'r' y 's''
            obs2, r, term, trunc, info = env.step(action)
            
            # Elige la SIGUIENTE acción 'a'' desde el nuevo estado 's''
            legal2 = np.flatnonzero(info["action_mask"])
            action2 = agent.act(obs2, legal2)
            
            # Ahora actualiza Q(s, a) usando (s, a, r, s', a')
            done = term or trunc
            agent.update(obs, action, r, obs2, action2, done)
            
            # Prepara la siguiente iteración
            obs = obs2
            action = action2
    return agent

def objective(trial, train_episodes, max_steps):
    """Función objetivo para un trial de Optuna."""
    params = {
        "alpha":     trial.suggest_float("alpha",     0.05, 0.6, log=True),
        "gamma":     trial.suggest_float("gamma",     0.90, 0.999),
        "eps_start": trial.suggest_float("eps0",      0.5,  1.0),
        "eps_end":   trial.suggest_float("eps_end",   0.01, 0.2),
        "eps_decay": trial.suggest_int(  "eps_decay", 1000, 10000),
    }

    env = PokemonEnv(max_steps=max_steps)
    seeds = [11, 29, 97]
    scores = []

    for i, seed in enumerate(seeds, 1):
        agent = TabularSarsaLearner(n_actions=env.action_space.n, **params)
        agent = train_agent(agent, env, train_episodes, seed)
        score = evaluate_greedy(env, agent, episodes=100, seed=seed + 999)
        
        scores.append(score)
        trial.report(float(np.mean(scores)), step=i)
        if trial.should_prune():
            raise optuna.exceptions.TrialPruned()
            
    return float(np.mean(scores))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=40, help="Número de trials de Optuna.")
    ap.add_argument("--train-episodes", type=int, default=600, help="Episodios de entrenamiento por trial.")
    ap.add_argument("--final-train-episodes", type=int, default=800, help="Episodios para el reentrenamiento final.")
    ap.add_argument("--study-name", type=str, default="sarsa-pokemon-study", help="Nombre del estudio.")
    ap.add_argument("--storage-db", type=str, default="sqlite:///optuna_studies.db", help="Base de datos para guardar el estudio.")
    args = ap.parse_args()

    pruner = optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=1)
    sampler = optuna.samplers.TPESampler(seed=42)
    
    study = optuna.create_study(
        direction="maximize",
        sampler=sampler,
        pruner=pruner,
        study_name=args.study_name,
        storage=args.storage_db,
        load_if_exists=True
    )

    study.optimize(
        lambda trial: objective(trial, args.train_episodes, max_steps=200),
        n_trials=args.trials,
        n_jobs=1,
        show_progress_bar=True
    )

    print("Estudio completado.")
    print("Mejor valor (win rate):", study.best_value)
    print("Mejores hiperparámetros:", study.best_params)

    print("\nReentrenando el mejor agente...")
    best_params = study.best_params
    env = PokemonEnv(max_steps=200)
    
    # --- Pequeño ajuste aquí para que los nombres de los parámetros coincidan ---
    final_agent = TabularSarsaLearner(
        n_actions=env.action_space.n,
        alpha=best_params["alpha"],
        gamma=best_params["gamma"],
        eps_start=best_params["eps0"], 
        eps_end=best_params["eps_end"],
        eps_decay=best_params["eps_decay"]
    )
    
    final_agent = train_agent(final_agent, env, args.final_train_episodes, seed=42)

    os.makedirs("checkpoints", exist_ok=True)
    # He cambiado el nombre del archivo para que sea más específico
    save_checkpoint(final_agent, env, "checkpoints/best_sarsa_agent.pkl")
    print("Mejor agente guardado en checkpoints/best_sarsa_agent.pkl")
    
    try:
        if optuna.visualization.is_available():
            fig = optuna.visualization.plot_optimization_history(study)
            fig.show()
            fig = optuna.visualization.plot_param_importances(study)
            fig.show()
    except ImportError:
        print("\nPara visualizar los resultados, instala plotly y kaleido: pip install plotly kaleido")


if __name__ == "__main__":
    main()