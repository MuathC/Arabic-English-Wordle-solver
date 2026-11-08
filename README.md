# 🧠 Arabic–English Wordle AI Solver

A **bilingual AI-powered Wordle solver** supporting **English and Arabic**, built to compare and evaluate multiple intelligent decision-making strategies.

This project explores how different AI techniques perform when solving Wordle-like games, with a strong focus on **information theory, probabilistic reasoning, and constraint satisfaction** — all wrapped in a playable application.

---

## 🚀 Key Features

- 🌍 **Bilingual Support**: English & Arabic Wordle
- 🤖 **Four AI Agents**:
  - Constraint Satisfaction (CSP)
  - Letter Frequency Heuristics
  - Bayesian Updating
  - Entropy Maximization (Information Gain)
- 📊 **Performance Evaluation**: Win rate, guess efficiency, and runtime
- 🧪 **Agent-vs-Agent & Human Comparison**
- ⚡ Optimized with caching for entropy computations

---

## 🖼️ Demo & Visuals

### 🔤 English Mode – AI Agent Comparison
*Side-by-side comparison of AI agents solving English Wordle*

![English Agent Comparison](images/english_agents.png)

---

### 🧑‍💻 Arabic Mode – Playing Against the AI
*Human player competing against the AI solver in Arabic Wordle*

![Arabic Human vs AI](images/arabic_vs_human.png)

---

### 🧪 Arabic Mode – AI Stress Testing
*Testing AI robustness and decision-making in Arabic Wordle*

![Arabic AI Testing](images/arabic_testing.png)

---

## 🏆 Performance Summary

| Agent | Win Rate | Avg. Guesses | Avg. Time |
|------|---------|--------------|-----------|
| **Entropy Maximization** | **100%** | **3.92** | 6.47s |
| Frequency Heuristic | 95.63% | 4.04 | 0.04s |
| CSP | 94.99% | 4.40 | 0.03s |
| Bayesian | 94.81% | 4.40 | 0.52s |

> **Insight:**  
> The Entropy agent consistently minimizes guesses by maximizing expected information gain, at the cost of higher computation time.

---

## 🛠️ Tech Stack

- Python
- NumPy / Pandas
- Probability & Information Theory
- Constraint Solving
- Custom Arabic word datasets
- Flask + plain HTML/CSS/JavaScript for the web app

---

## 🌐 Web App

The solver also runs in the browser, using the same agents and word lists as the desktop app:

- **Play vs Agent**: guess the hidden word in English or Arabic (right-to-left). **Hint** asks the selected agent for its next guess on your board. When you finish, the agent plays the same word and the page says who did better.
- **Test Agent**: pick a word (or a random one), then step through the agent's guesses with **Next guess** or let it **Solve**.
- **Comparison**: all four agents solve the same word side by side, with their guess counts and time.

From the repository root, after installing the requirements:

```bash
pip install -r requirements.txt
python -m web.app
```

Then open http://127.0.0.1:8000 (set `PORT` to use another port). Games live in memory in a single Flask process, so restarting the server clears them. The Entropy agent can take several seconds per guess, mostly on its second guess in Arabic.

Run the tests with:

```bash
python -m pytest
```

---

## ⚙️ Setup & Installation

### 1️⃣ Create a Virtual Environment

**Windows**
```powershell
py -m venv .venv
