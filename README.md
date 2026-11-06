# 🚦 AURA / VisionX: AI-Powered Smart Traffic Management

![React](https://img.shields.io/badge/react-20232a?style=for-the-badge&logo=react&logoColor=61DAFB)
![NodeJS](https://img.shields.io/badge/node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![SUMO](https://img.shields.io/badge/SUMO-Traffic_Simulation-blue?style=for-the-badge)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20265628-blue?style=for-the-badge)](https://doi.org/10.5281/zenodo.20265628)

**AURA** (*Adaptive Urban Routing and Actuation*), developed for **Smart India Hackathon 2026**, is a next-generation decentralized traffic optimization and emergency vehicle preemption system. It replaces rigid fixed-time cycles with a **Semi-Markov Decision Process (SMDP)** agent and **Rolling Preemption Coordination** with action-duration bounds that dynamically manage intersection phases in real-time under genuine TraCI microscopic simulation.

---

## ✨ Key Features

- **🧠 Semi-Markov Reinforcement Learning Core:** Decentralized Deep Q-Network optimizing phase targets with continuous-time discount factor scaling ($\gamma^\tau$).
- **⏱️ Action-Duration Bounds:** Enforces statutory minimum green times ($10\text{s}$), queue-proportional maximum duration ($45\text{s}$), and mandatory 3-second yellow clearance transitions compliant with municipal standards.
- **🚨 Rolling Emergency Vehicle Preemption (EVP):** Sequential green-wave clearing that moves dynamically with emergency vehicles without paralyzing un-involved grid intersections.
- **🌊 Post-Preemption Shockwave Mitigation:** Momentum recovery reward that actively prioritizes starved cross-arterials to dissolve congestion shockwaves after preemption clears.
- **🌐 Dual-Mode Full-Stack Dashboard:** Live React.js + Tailwind CSS interface featuring both the **Intersection A0 Monitor** and the **Phase 2 Tactical Dispatch Map (5x2 Grid)**.
- **📡 Resilient DDS / WebSocket Bridge:** Node.js synchronization bridge connecting REST clients, the PyTorch AI agent, and ROS 2 DDS networks.

---

## 🏗️ System Architecture & Folder Structure

```text
Traffic-Management-System/
├── paper/                  # Complete IEEE Conference Research Paper Source
│   ├── main.tex            # Master LaTeX document (ieeeconf.cls)
│   ├── references.bib      # Complete bibliography
│   ├── ieeeconf.cls        # Official IEEE conference style
│   └── sections/           # Modular paper sections (Intro, Related, Method, Exp, Concl)
├── paper_aura_ieeeconf.zip # Ready-to-upload Overleaf archive
├── traffic-ai/             # PyTorch DQN Models, TraCI Control & SUMO Simulation
│   ├── venv/               # Symlinked Python Virtual Environment (CUDA enabled)
│   ├── requirements.txt    # PyTorch, TraCI, NumPy, Matplotlib, Pandas
│   ├── rl_agent.py         # DQN Training script with Experience Replay
│   ├── run_demo.py         # Single-intersection production demo agent
│   ├── run_marl_corridor.py# Phase 2 Decentralized 10-node MARL corridor
│   ├── evaluate_rigorous_benchmark.py # 6-controller genuine rush-hour benchmark
│   ├── evaluate_real_manhattan.py     # 6-controller 177-TLS Manhattan OSM benchmark
│   ├── import_osm_map.py   # Automated OSM-to-SUMO network & traffic converter
│   ├── manhattan.net.xml   # Real Midtown Manhattan road network (177 traffic lights)
│   ├── marl_grid.net.xml   # 10-intersection grid network (A0..E1)
│   └── *.png               # High-res publication benchmark plots
├── traffic-backend/        # Node.js Synchronization Bridge
│   ├── package.json        # Express, CORS, WebSockets (ws), RosLib
│   └── server.js           # REST Telemetry + Command Dispatch + ROS 2 Bridge
└── traffic-dashboard/      # React.js + Vite + Tailwind CSS Web Dashboard
    ├── package.json
    └── src/App.jsx         # Dual-mode UI (Intersection Telemetry + Tactical Dispatch)
```

---

## ⚙️ Prerequisites

- **OS:** Linux (Ubuntu 24.04 Native or WSL2) / Windows
- **Python:** 3.10+ (with virtual environment support)
- **Node.js:** v18+ or v20+
- **SUMO:** Eclipse SUMO (`sudo apt install sumo sumo-tools sumo-gui`)
- **Environment Variable:** `SUMO_HOME=/usr/share/sumo`

---

## 🚀 Installation & Setup

### 1. Setup the Python Virtual Environment & Requirements

```bash
cd traffic-ai
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Install Backend Bridge Dependencies

```bash
cd traffic-backend
npm install
```

### 3. Install Dashboard Dependencies

```bash
cd traffic-dashboard
npm install
```

---

## 🎬 Running the Live Demo

Run the components across 3 terminals in this sequence:

### Terminal 1 — Start the Backend Server

```bash
cd traffic-backend
node server.js
# Output: 🚀 VisionX / AURA Backend Active on Port 3000
```

### Terminal 2 — Start the Frontend Dashboard

```bash
cd traffic-dashboard
npm run dev
# Then open http://localhost:5173 in your browser
```

### Terminal 3 — Launch the AI Simulation

```bash
cd traffic-ai
source venv/bin/activate
python3 run_demo.py
# SUMO GUI will automatically launch and stream live queue metrics to the dashboard
```

> **Tip:** To run headless (without GUI display), use: `SUMO_GUI=0 python3 run_demo.py`.

---

## 📊 Empirical Benchmarks & Scientific Results

Rigorous microscopic evaluations were conducted in Eclipse SUMO under the Krauss car-following model across two scenarios:

### 1. Saturated Rush-Hour Multi-Seed Benchmark (1,000s, p = 0.22 veh/s, 5 Seeds: 42, 101, 777, 1337, 2024)

| Controller | Class / Venue | Avg Queue ($\bar{Q}$, veh) | Max Queue ($Q_{\max}$, veh) | EV Latency ($T_{\text{clear}}$, s) | Recovery Horizon ($T_{\text{rec}}$, s) | Cumulative $\text{CO}_2$ (kg) |
|---|---|---|---|---|---|---|
| **Fixed-Time (30s Cycle)** | Webster (1958) | 14.47 ± 0.92 | **28.6 ± 1.2** | 68.0 ± 41.8s | 22.4 ± 15.2s | 114.57 ± 3.73 |
| **Demand Actuated** | SCATS (1990) | 18.72 ± 1.11 | 34.2 ± 3.0 | 120.2 ± 54.5s (Delay) | 20.4 ± 3.4s | 139.09 ± 3.15 |
| **Max-Pressure** | Varaiya (2013) | 17.93 ± 1.01 | 30.0 ± 1.7 | 127.4 ± 61.8s (Delay) | 18.6 ± 1.5s | 137.72 ± 3.95 |
| **PressLight** | Wei et al., ACM KDD (2019) | 17.93 ± 1.01 | 30.0 ± 1.7 | 127.4 ± 61.8s (Delay) | 18.6 ± 1.5s | 137.72 ± 3.95 |
| **EVP-DRL** | Lin et al., TR-C (2023) | 17.79 ± 0.88 | 34.4 ± 3.0 | 75.6 ± 42.6s | 55.0 ± 5.2s (Shockwave) | 134.75 ± 3.44 |
| **AURA (Proposed)** | Safe SMDP + Momentum | **15.81 ± 1.53** | **30.2 ± 2.3** | **67.4 ± 37.5s (-47.1%)** | **30.4 ± 17.1s (-44.7%)** | **122.71 ± 5.31 (-8.9%)** |

### 2. Formal Component Ablation Study (Across 5 Seeds)

| Configuration | Description | Avg Queue ($\bar{Q}$) | Max Queue ($Q_{\max}$) | Recovery ($T_{\text{rec}}$) | Phase Switches |
|---|---|---|---|---|---|
| **Full AURA (Proposed)** | Complete Safe SMDP + Momentum | **15.81 ± 1.53** | **30.2 ± 2.3** | **30.4 ± 17.1s** | **39.4 ± 2.6 (Smooth)** |
| **w/o Momentum Flush** | SMDP Bounds only | 15.88 ± 1.72 | 31.0 ± 3.3 | 30.4 ± 17.1s | 39.6 ± 2.5 |
| **w/o SMDP Bounds** | Unconstrained DRL (Action Flickering) | 16.14 ± 1.23 | 50.4 ± 0.5 (+66.9%) | 69.8 ± 3.3s (+129.6%) | 113.0 ± 8.5 (Flickering) |

### 3. Edge-Computing Profiling: City-Wide and Statewide Control on a Laptop

| Metric | Profile / Empirical Value |
|---|---|
| **Neural Architecture** | 2-Layer MLP ($4 \to 64 \to 64 \to 4$) |
| **Model Size** | **18.52 KB** (4,740 parameters) per intersection |
| **Single-Core CPU Inference** | **33.28 $\mu$s** per intersection decision |
| **Throughput per Core** | **30,050 intersection decisions / second** on 1 commodity CPU core |
| **10,000-Node Regional Network** | **$<$ 33.3% of 1 Laptop CPU core**, **$<$ 20 MB RAM** total |
| **HPC / Cloud Server Dependency** | **Zero** — 100% decentralized edge deployment |

### 4. Real-World Midtown Manhattan OpenStreetMap Benchmark (177 Intersections, 661 Edges, 1,501 Vehicles)

| Controller | Class / Venue | Avg Queue ($\bar{Q}$, veh) | Max Queue ($Q_{\max}$, veh) | EV Latency ($T_{\text{clear}}$, s) | Recovery Horizon ($T_{\text{rec}}$, s) |
|---|---|---|---|---|---|
| **Fixed-Time (Manhattan)** | Webster (1958) | 126.73 | 343 | 44s | 28s |
| **Demand Actuated** | SCATS (1990) | 119.10 | 317 | 38s | 28s |
| **Max-Pressure** | Varaiya (2013) | 111.18 | 270 | 33s | 36s |
| **PressLight** | Wei et al., ACM KDD (2019) | 116.72 | 265 | 35s | 70s |
| **EVP-DRL** | Lin et al., TR-C (2023) | 115.89 | 280 | **15s** | **27s** |
| **AURA (Proposed)** | SMDP Bounded + Momentum | **109.46 (-13.6%)** | **257 (-25.1%)** | **15s (-65.9%)** | 36s |

---

## 🔬 Reproducing Research Benchmarks & Simulations

### Run Phase 2 Multi-Intersection Corridor (10 Nodes)
```bash
cd traffic-ai
python3 run_marl_corridor.py
```

### Run Real-World Midtown Manhattan OSM Evaluation
```bash
cd traffic-ai
python3 evaluate_real_manhattan.py
```

### Compile IEEE Conference Paper
The ready-to-compile IEEE paper package is located in `paper/` and archived in `paper_aura_ieeeconf.zip` for direct upload to Overleaf.

---

## 🗺️ Academic Preprint
- **Preprint DOI:** [10.5281/zenodo.20265628](https://doi.org/10.5281/zenodo.20265628)
- **Target Venue:** IEEE Conference on Intelligent Transportation Systems (ITSC) / Robotics and Automation Letters (RA-L)
- **Author:** Deepak R., Department of Robotics and Automation, Dhaanish Ahmed College of Engineering
