# Computer Simulation: Prisoner's Dilemma

A Binder-ready and JupyterBook-ready tutorial repository for learning computer simulation through the Prisoner's Dilemma.

The tutorial is inspired by the style of Methods Hub tutorials: practical, notebook-first, reproducible, and suitable for self-paced methods training.

## Contents

The tutorial uses four complementary simulation solutions:

1. **Direct payoff-matrix simulation**: deterministic one-shot and repeated games.
2. **Agent-based simulation**: simple agents using classic strategies.
3. **Monte Carlo tournament**: noisy repeated tournaments with uncertainty.
4. **Evolutionary simulation**: population dynamics using replicator-style selection.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

## Launch with Binder

Once this repository is on GitHub, use repo2binder or a Binder badge of the form:

```text
https://mybinder.org/v2/gh/<USER>/<REPO>/main?urlpath=lab/tree/notebooks/index.ipynb
```

## Build the JupyterBook locally

```bash
pip install -r requirements.txt
jupyter-book build .
```

The generated site will be in `_build/html/`.

## GitHub Pages

The workflow in `.github/workflows/deploy-book.yml` builds the book and deploys it to GitHub Pages. Configure repository Pages to deploy from GitHub Actions.

## Thebe

The JupyterBook configuration enables Thebe. On the published website, readers can connect code cells to a Binder-backed kernel and execute examples in the browser.
