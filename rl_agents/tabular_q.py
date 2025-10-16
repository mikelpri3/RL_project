import math, numpy as np
from collections import defaultdict

class TabularQLearner:
    def __init__(self, n_actions, alpha=0.3, gamma=0.99, eps_start=1.0, eps_end=0.05, eps_decay=3000):
        self.n_actions = n_actions
        self.alpha, self.gamma = alpha, gamma
        self.eps_start, self.eps_end, self.eps_decay = eps_start, eps_end, eps_decay
        self.Q = defaultdict(lambda: np.zeros(n_actions, dtype=np.float32))
        self.t = 0

    def _eps(self):
        return self.eps_end + (self.eps_start - self.eps_end) * math.exp(-self.t / self.eps_decay)

    def act(self, s, legal_actions):
        eps = self._eps()
        if np.random.rand() < eps:
            return int(np.random.choice(list(legal_actions)))
        return int(np.argmax(self.Q[s]))

    def update(self, s, a, r, s2, done):
        self.t += 1
        q = self.Q[s][a]
        target = r if done else r + self.gamma * float(np.max(self.Q[s2]))
        self.Q[s][a] = q + self.alpha * (target - q)
