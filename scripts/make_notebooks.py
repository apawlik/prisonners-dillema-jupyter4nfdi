import nbformat as nbf
from pathlib import Path

NOTEBOOKS = Path('notebooks')
NOTEBOOKS.mkdir(exist_ok=True)

def nb(path, cells):
    notebook = nbf.v4.new_notebook()
    notebook['cells'] = cells
    notebook['metadata'] = {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'pygments_lexer': 'ipython3'},
    }
    nbf.write(notebook, NOTEBOOKS / path)

def md(s): return nbf.v4.new_markdown_cell(s)
def code(s): return nbf.v4.new_code_cell(s)

common = """import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nsns.set_theme(style='whitegrid')\n"""

nb('index.ipynb', [
md("""# Computer Simulation: Prisoner's Dilemma\n\nThis tutorial introduces computer simulation through the Prisoner's Dilemma, a compact model of cooperation, conflict, institutions, and repeated interaction. It follows a practical notebook-first format suitable for methods teaching.\n\n## Learning goals\n\nBy the end you will be able to:\n\n- represent a social-science model as executable code;\n- compare deterministic, agent-based, Monte Carlo, and evolutionary simulations;\n- visualise simulation output;\n- discuss what each computational solution does and does not explain.\n\n## Four simulation solutions\n\n1. Payoff-matrix simulation.\n2. Agent-based simulation.\n3. Monte Carlo tournament.\n4. Evolutionary population simulation.\n\nUse the rocket or Thebe button in the online book to run cells through Binder.\n"""),
code("print('Welcome to the Prisoner\\'s Dilemma simulation tutorial!')")
])

nb('01_payoff_matrix.ipynb', [
md("""# 1. Direct payoff-matrix simulation\n\nThe classic Prisoner's Dilemma has two actions: cooperate (`C`) or defect (`D`). A common payoff ordering is temptation `T=5`, reward `R=3`, punishment `P=1`, sucker payoff `S=0`, where `T > R > P > S`.\n\nThis first solution encodes the model directly as a payoff table and simulates one-shot and repeated play."""),
code(common + "\npayoffs = {('C','C'):(3,3), ('C','D'):(0,5), ('D','C'):(5,0), ('D','D'):(1,1)}\ndef play(a, b):\n    return payoffs[(a, b)]\n\nrows = []\nfor a in ['C','D']:\n    for b in ['C','D']:\n        rows.append({'player_a': a, 'player_b': b, 'payoff_a': play(a,b)[0], 'payoff_b': play(a,b)[1]})\npd.DataFrame(rows)"),
md("""## Repeated play\n\nRepeated interactions let us ask how the same rule performs over time."""),
code("""def simulate_pair(strategy_a, strategy_b, rounds=20):\n    history = []\n    for t in range(rounds):\n        a = strategy_a(history, player=0)\n        b = strategy_b(history, player=1)\n        pa, pb = play(a, b)\n        history.append((a, b, pa, pb))\n    return pd.DataFrame(history, columns=['a','b','payoff_a','payoff_b'])\n\ndef always_c(history, player): return 'C'\ndef always_d(history, player): return 'D'\n\ndf = simulate_pair(always_c, always_d, 10)\ndf.assign(cum_a=df.payoff_a.cumsum(), cum_b=df.payoff_b.cumsum())"""),
code("""result = simulate_pair(always_c, always_d, 20)\nresult[['payoff_a','payoff_b']].cumsum().plot(title='Cumulative payoff: Always Cooperate vs Always Defect')\nplt.xlabel('Round'); plt.ylabel('Cumulative payoff');""")
])

nb('02_agent_based.ipynb', [
md("""# 2. Agent-based simulation\n\nAgent-based simulation represents decision makers as agents with simple behavioural rules. Here we compare classic strategies: always cooperate, always defect, tit-for-tat, and random."""),
code(common + "\npayoffs = {('C','C'):(3,3), ('C','D'):(0,5), ('D','C'):(5,0), ('D','D'):(1,1)}\ndef score(a,b): return payoffs[(a,b)]"),
code("""class Strategy:\n    name = 'base'\n    def move(self, own, other): raise NotImplementedError\nclass AlwaysCooperate(Strategy):\n    name = 'always cooperate'\n    def move(self, own, other): return 'C'\nclass AlwaysDefect(Strategy):\n    name = 'always defect'\n    def move(self, own, other): return 'D'\nclass TitForTat(Strategy):\n    name = 'tit for tat'\n    def move(self, own, other): return 'C' if not other else other[-1]\nclass RandomStrategy(Strategy):\n    name = 'random'\n    def move(self, own, other): return np.random.choice(['C','D'])\n\ndef match(s1, s2, rounds=50):\n    h1, h2, p1, p2 = [], [], 0, 0\n    for _ in range(rounds):\n        a, b = s1.move(h1,h2), s2.move(h2,h1)\n        x, y = score(a,b); h1.append(a); h2.append(b); p1 += x; p2 += y\n    return p1, p2\n\nstrategies = [AlwaysCooperate(), AlwaysDefect(), TitForTat(), RandomStrategy()]\nrecords=[]\nfor s1 in strategies:\n    for s2 in strategies:\n        p1,p2 = match(s1,s2)\n        records.append({'row_strategy':s1.name,'column_strategy':s2.name,'row_payoff':p1,'column_payoff':p2})\ndf = pd.DataFrame(records)\ndf.pivot(index='row_strategy', columns='column_strategy', values='row_payoff')"""),
code("""sns.heatmap(df.pivot(index='row_strategy', columns='column_strategy', values='row_payoff'), annot=True, fmt='.0f', cmap='viridis')\nplt.title('Agent strategy tournament: row payoff');""")
])

nb('03_monte_carlo_tournament.ipynb', [
md("""# 3. Monte Carlo tournament\n\nMonte Carlo simulation repeats the same experiment many times while sampling random events. We introduce implementation error: intended actions sometimes flip."""),
code(common + "\npayoffs = {('C','C'):(3,3), ('C','D'):(0,5), ('D','C'):(5,0), ('D','D'):(1,1)}\ndef noisy(action, error=0.05):\n    return ('D' if action == 'C' else 'C') if np.random.random() < error else action"),
code("""def run(strategy_a, strategy_b, rounds=100, error=0.05):\n    ha, hb, pa, pb = [], [], 0, 0\n    for _ in range(rounds):\n        a = noisy(strategy_a(ha,hb), error); b = noisy(strategy_b(hb,ha), error)\n        x,y = payoffs[(a,b)]; ha.append(a); hb.append(b); pa += x; pb += y\n    return pa, pb\n\ndef ac(own, other): return 'C'\ndef ad(own, other): return 'D'\ndef tft(own, other): return 'C' if len(other)==0 else other[-1]\ndef rand(own, other): return np.random.choice(['C','D'])\nstrategies = {'always cooperate':ac, 'always defect':ad, 'tit for tat':tft, 'random':rand}\n\nrecords=[]\nfor rep in range(500):\n    for name, strat in strategies.items():\n        opponents = [v for k,v in strategies.items() if k != name]\n        total = sum(run(strat, opp, error=0.05)[0] for opp in opponents)\n        records.append({'replication':rep, 'strategy':name, 'payoff':total})\nmc = pd.DataFrame(records)\nmc.groupby('strategy').payoff.describe()"""),
code("""sns.boxplot(data=mc, x='payoff', y='strategy')\nplt.title('Monte Carlo tournament under action error');""")
])

nb('04_evolutionary_simulation.ipynb', [
md("""# 4. Evolutionary simulation\n\nEvolutionary simulation asks how the share of strategies changes when better-performing strategies become more common. This solution is useful for modelling adaptation without assuming fully rational actors."""),
code(common + "\npayoff_matrix = pd.DataFrame(\n    [[3,0,3,1.5],[5,1,1.2,3],[3,0.8,3,2],[3.5,1,2.5,2.25]],\n    index=['cooperate','defect','tit_for_tat','random'],\n    columns=['cooperate','defect','tit_for_tat','random']\n)\npayoff_matrix"),
code("""def replicator(initial, generations=60):\n    shares = np.array(initial, dtype=float) / np.sum(initial)\n    history = [shares.copy()]\n    A = payoff_matrix.values\n    for _ in range(generations):\n        fitness = A @ shares\n        avg = shares @ fitness\n        shares = shares * fitness / avg\n        shares = shares / shares.sum()\n        history.append(shares.copy())\n    return pd.DataFrame(history, columns=payoff_matrix.index).rename_axis('generation').reset_index()\n\nevo = replicator([0.25,0.25,0.25,0.25])\nevo.tail()"""),
code("""evo.set_index('generation').plot(figsize=(8,4))\nplt.ylabel('Population share')\nplt.title('Evolutionary dynamics among strategies');""")
])

nb('05_comparing_solutions.ipynb', [
md("""# 5. Comparing the four solutions\n\nEach simulation solution answers a different kind of question.\n\n| Solution | Best for | Main limitation |\n|---|---|---|\n| Payoff matrix | Understanding the formal model | Too simple for heterogeneous behaviour |\n| Agent-based | Explicit behavioural rules | Results depend on chosen rules |\n| Monte Carlo | Uncertainty and robustness | Computational summaries can hide mechanisms |\n| Evolutionary | Population-level adaptation | Fitness assumptions can be strong |\n\n## Suggested exercises\n\n1. Change the payoff values. When does cooperation become easier?\n2. Add a new strategy, such as grim trigger.\n3. Increase the Monte Carlo error rate. Which strategy is most robust?\n4. Change the evolutionary starting population. Do you reach the same endpoint?\n"""),
code("""import pandas as pd\nsummary = pd.DataFrame({\n    'solution':['payoff matrix','agent-based','Monte Carlo','evolutionary'],\n    'unit':['action profile','agent pair','repeated random experiment','population share'],\n    'output':['payoff table/time series','strategy tournament','payoff distribution','trajectory over generations']\n})\nsummary""")
])

print('notebooks written')
