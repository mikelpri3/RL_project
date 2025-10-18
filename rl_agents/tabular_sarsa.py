import math, numpy as np
from collections import defaultdict


# We implemented SARSA algorithm in order to compare it against the Q-Learning

class TabularSarsaLearner:
    def __init__(self, n_actions, alpha=0.3, gamma=0.99, eps_start=1.0, eps_end=0.05, eps_decay=3000):
        self.n_actions = n_actions
        self.alpha, self.gamma = alpha, gamma
        self.eps_start, self.eps_end, self.eps_decay = eps_start, eps_end, eps_decay
        self.Q = defaultdict(lambda: np.zeros(n_actions, dtype=np.float32))
        self.t = 0

    def _eps(self):
        """
        Typical schedule to control exploration vs exploitation.
        This prevents the agent from getting stuck early in suboptimal behaviors.
        We want high exploration at first, then reduce it gradually.
        
        eps_start = 1.0 (100% random initially)
        eps_end = 0.05 (mostly greedy later)
        eps_decay = how fast it decays (larger → slower decay)
        """
        return self.eps_end + (self.eps_start - self.eps_end) * math.exp(-self.t / self.eps_decay)

    def act(self, s, legal_actions):
        eps = self._eps()
        self.t += 1
        legal = np.array(list(legal_actions), dtype=int)

        # Handle case where there are no legal actions
        if not legal.size:
            return 0 # Return a default action, e.g., action '0'
        
        if np.random.rand() < eps:
            return int(np.random.choice(legal))           # explore among legal
        
        q_values = self.Q[s]
        # exploit among legal: argmax on the legal slice
        return int(legal[np.argmax(q_values[legal])])

    def update(self, s, a, r, s2, a2, done):
        """
        SARSA UPDATE RULE
        Uses the tuple (s, a, r, s2, a2)
        """
        q_current = self.Q[s][a]
        
        # SARSA's core difference from Q-learning is right here.
        # If the episode is done, the target is just the reward.
        # Otherwise, the target includes the Q-value of the *actual next action (a2)*.
        if done:
            target = r
        else:
            # We use Q[s2][a2], NOT max(Q[s2])
            q_next = self.Q[s2][a2]
            target = r + self.gamma * q_next
            
        # Standard TD update
        self.Q[s][a] = q_current + self.alpha * (target - q_current)