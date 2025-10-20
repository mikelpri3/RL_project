# utils/checkpoint.py
import pickle, numpy as np
from collections import defaultdict

def save_checkpoint(agent, env, path: str):
    # agent.Q: defaultdict(int -> np.ndarray)
    # env.encoder.*: the ID<->TinyState maps
    payload = {
        "Q": {int(k): v for k, v in agent.Q.items()},                 # visited rows only
        "encoder_from_id": {int(k): env.encoder.from_id[k] for k in env.encoder.from_id},
        # you could reconstruct to_id from from_id, so we don’t store it twice
    }
    with open(path, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_checkpoint(agent, env, path: str):
    with open(path, "rb") as f:
        payload = pickle.load(f)
    # restore Q as defaultdict again (so unseen states still auto-init)
    agent.Q = defaultdict(lambda: np.zeros(agent.n_actions, dtype=np.float32), payload["Q"])
    # rebuild encoder maps
    env.encoder.to_id.clear()
    env.encoder.from_id.clear()
    for sid, tiny in payload["encoder_from_id"].items():
        env.encoder.from_id[sid] = tiny
        env.encoder.to_id[tiny] = sid
