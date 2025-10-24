import numpy as np, os, argparse, csv, time
from rl_env.pokemon_env import PokemonEnv
from rl_agents.tabular_q import TabularQLearner
from utils.checkpoint import save_checkpoint, load_checkpoint
import datetime

CKPT_DEFAULT = "checkpoints/q_table.pkl"

# ---------- Greedy evaluation (ε = 0) ----------
def evaluate_greedy(env: PokemonEnv, agent: TabularQLearner, episodes: int = 50, seed: int = 123):
    """
    Runs episodes with a purely greedy policy (no exploration, no learning).
    Returns the win-rate in [0,1].
    """
    rng = np.random.default_rng(seed)
    wins, rets = 0, []
    for _ in range(episodes):
        # re-seed env for reproducibility across evals (optional)
        obs, info = env.reset(seed=int(rng.integers(1_000_000)))
        terminated = truncated = False
        G = 0.0
        while not (terminated or truncated):
            legal = np.flatnonzero(info["action_mask"])
            q = agent.Q[obs]  # shape: [n_actions]
            # greedy among legal; guard in case q shorter than action_space.n
            a = int(legal[np.argmax(q[legal])]) if len(legal) else 0
            obs, r, terminated, truncated, info = env.step(a)
            G += r
        rets.append(G)
        if terminated and env.battle.winner() == "agent": #little change here to improve reward
            wins += 1
    return wins / episodes, float(np.mean(rets))

def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=1000)
    ap.add_argument("--eval-every", type=int, default=50)
    ap.add_argument("--ckpt", type=str, default=CKPT_DEFAULT)
    ap.add_argument("--load", action="store_true", help="load checkpoint if exists")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--log-csv", type=str, default="logs/train_log_{timestamp}.csv".format(timestamp=timestamp))
    ap.add_argument("--alpha", type=float, default=0.30)
    ap.add_argument("--gamma", type=float, default=0.99)
    ap.add_argument("--eps-start", type=float, default=1.0)
    ap.add_argument("--eps-end", type=float, default=0.05)
    ap.add_argument("--eps-decay", type=int, default=4000)
    args = ap.parse_args()

    os.makedirs("checkpoints", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # ----- env & agent -----
    env = PokemonEnv(max_steps=200)
    agent = TabularQLearner(
        n_actions=env.action_space.n,
        alpha=args.alpha, gamma=args.gamma,
        eps_start=args.eps_start, eps_end=args.eps_end, eps_decay=args.eps_decay)

    csvf = open(args.log_csv, "w", newline="")
    writer = csv.writer(csvf)
    writer.writerow(["episode","train_return","steps","epsilon","q_rows","eval_winrate","eval_return"])

    t0 = time.time()
    # ----- training loop with periodic evaluation -----

    for ep in range(1, args.episodes + 1):
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
        # periodic greedy eval + save
        eval_wr = eval_ret = float("nan")

        if ep % args.eval_every == 0:
            eval_wr, eval_ret = evaluate_greedy(env, agent, episodes=100)
            save_checkpoint(agent, env, args.ckpt)
            if args.verbose:
                elapsed = time.time() - t0
                print(f"[ep {ep:4d}] train_return={G:7.3f} steps={steps:3d} "
                      f"eps={agent._eps():.3f} Qrows={len(agent.Q)} "
                      f"| eval wr={eval_wr:.2f} ret={eval_ret:.3f} | {elapsed:.1f}s")

        writer.writerow([ep, f"{G:.4f}", steps,
                         f"{agent._eps():.6f}", len(agent.Q),
                         f"{eval_wr:.4f}" if eval_wr==eval_wr else "",
                         f"{eval_ret:.4f}" if eval_ret==eval_ret else ""])
        csvf.flush()

    csvf.close()
    print(f"[done] CSV log -> {args.log_csv}")

if __name__ == "__main__":
    main()
