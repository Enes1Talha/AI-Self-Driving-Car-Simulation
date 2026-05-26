# 🚗 AI Self-Driving Car Simulation with NEAT

> A Python-based autonomous driving simulation where a neural network evolves from zero driving ability to lap-completing behaviour through the **NEAT (NeuroEvolution of Augmenting Topologies)** algorithm.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-Simulation-green)
![NEAT](https://img.shields.io/badge/Algorithm-NEAT-orange)

---

## 📌 Project Overview

This project implements a real-time neuroevolution simulation in which 100 AI-controlled cars learn to navigate a closed oval track with obstacles. Starting from random neural networks, successive generations of cars are bred, mutated, and selected — demonstrating emergent driving behaviour without any hand-coded rules.

The project was built to explore how **evolutionary algorithms** can solve control problems that are difficult to approach with supervised learning due to the lack of labelled training data.

---

## 🧠 How It Works

### Neural Network Architecture
Each car is controlled by a feed-forward neural network:
- **Inputs (7):** Radar distance readings at angles `[-120°, -90°, -45°, 0°, 45°, 90°, 120°]`, each normalised to `[0, 1]`
- **Hidden layer:** 4 nodes with `tanh` activation
- **Outputs (4):** Turn left, turn right, decelerate, accelerate

### NEAT Evolutionary Loop
1. **Initialisation:** Population of 100 cars with random networks
2. **Simulation:** Each car drives until it crashes, idles for too long, or the generation timer expires (40s)
3. **Fitness Evaluation:** Fitness is accumulated based on speed, checkpoint passing, and lap completion
4. **Selection & Reproduction:** Top-performing genomes survive (elitism=10), offspring are created via crossover and mutation
5. **Speciation:** Genetically similar networks are grouped; stagnant species are pruned after 20 generations

### Fitness Function Design
| Event | Fitness Change |
|---|---|
| Each tick at speed > 0 | `+speed × 0.1` |
| Passing mid-track checkpoint | `+2,000` |
| Completing a full lap | `+10,000` |
| Idling (speed < 3 after 100 ticks) | `-10` |

The two-checkpoint system (mid-track + finish line) prevents shortcut exploitation — a car cannot score the lap bonus without first passing the midpoint.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Core language |
| Pygame | Real-time 2D simulation & rendering |
| NEAT-Python | Evolutionary neural network library |

---

## 🚀 Installation & Run

```bash
# 1. Clone the repository
git clone https://github.com/Enes1Talha/AI-Self-Driving-Car-Simulation.git
cd AI-Self-Driving-Car-Simulation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the simulation
python main.py
```

> **Note:** The NEAT config file (`config.txt`) is auto-generated on first run.

---

## 📈 Observed Evolution Progression

| Generation | Behaviour |
|---|---|
| 0–2 | Complete chaos — random steering, immediate crashes |
| 3 | First car successfully completes a lap |
| 10+ | Consistent lap completion; obstacle avoidance emerges |
| 30+ | Swarm-like synchronised behaviour; near-optimal racing lines |

---

## ⚙️ Key NEAT Configuration

```ini
pop_size        = 100
elitism         = 10          # Top 10 genomes survive unchanged
survival_threshold = 0.1      # Only top 10% reproduce
max_stagnation  = 20          # Species pruned after 20 stagnant generations
conn_add_prob   = 0.5         # Probability of adding a new connection
node_add_prob   = 0.2         # Probability of adding a new node
weight_mutate_rate = 0.8      # High mutation rate encourages exploration
```

---

## 💡 Key Learnings & Challenges

- **Reward shaping is critical:** An early version rewarded only distance travelled, leading cars to drive in circles. Adding the two-checkpoint system forced directional progress.
- **Speciation prevents premature convergence:** Without it, the population quickly collapsed to a single dominant genotype, losing genetic diversity.
- **Sensor angle selection matters:** Symmetrical radar angles (±45°, ±90°, ±120°) gave better cornering performance than asymmetric configurations.

---

## 🔮 Potential Extensions

- [ ] More complex track layouts (S-curves, chicanes)
- [ ] Multi-objective fitness (speed vs. smoothness)
- [ ] Visualisation of the evolved network topology
- [ ] Comparison with a Deep Q-Network (DQN) baseline

---

*Developed by [Enes Talha](https://github.com/Enes1Talha)*
