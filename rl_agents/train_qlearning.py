from rl_env.pokemon_env import PokemonEnv
from rl_agents.tabular_q import TabularQLearner

env = PokemonEnv()
agent = TabularQLearner(n_actions=env.action_space_n)

for ep in range(1000):
    s = env.reset()
    done = False
    G = 0.0
    steps = 0
    while not done:
        legal = set(env.battle.acciones_legales_agente())
        a = agent.act(s, legal)
        s2, r, done, _ = env.step(a)
        agent.update(s, a, r, s2, done)
        s, G = s2, G + r
        steps += 1
    if ep % 50 == 0:
        print(f"ep={ep:4d} return={G:6.2f} steps={steps}")
