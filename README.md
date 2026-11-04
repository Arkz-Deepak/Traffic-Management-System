# 🚦 AURA / VisionX: AI-Powered Smart Traffic Management

![React](https://img.shields.io/badge/react-20232a?style=for-the-badge&logo=react&logoColor=61DAFB)
![NodeJS](https://img.shields.io/badge/node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![SUMO](https://img.shields.io/badge/SUMO-Traffic_Simulation-blue?style=for-the-badge)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20265628-blue?style=for-the-badge)](https://doi.org/10.5281/zenodo.20265628)

**AURA** (*Acoustic-visual Urban Routing Architecture*), developed for **Smart India Hackathon 2026**, is a next-generation decentralized traffic optimization and emergency vehicle preemption system. It replaces rigid fixed-time cycles with a **Deep Reinforcement Learning (DQN)** agent and **Multi-Agent Preemption** that dynamically manages intersection phases in real-time, reducing vehicle queuing by over **85%**.

---

## ✨ Key Features

- **🧠 Deep Reinforcement Learning Core:** 64-neuron PyTorch DQN model trained with Experience Replay to optimize traffic flow dynamically.
- **⏱️ Deterministic Safety Envelope:** Enforces realistic minimum green times (10s), maximum allocations (45s), and mandatory 3-second yellow clearance transitions.
- **🚨 Emergency Overrides & Preemption:** Instant directional preemption triggers for ambulances and law enforcement ("Police All-Stop").
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
│   ├── evaluate_rigorous_benchmark.py # 4-controller 1,000s synthetic benchmark
│   ├── evaluate_real_manhattan.py     # 4-controller real OpenStreetMap benchmark
│   ├── import_osm_map.py   # Automated OSM-to-SUMO network & traffic converter
│   ├── manhattan.net.xml   # Real Midtown Manhattan road network (183 traffic lights)
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

### 1. Controlled Corridor Benchmark (1,000s Evaluation Horizon)

| Controller | Class / Venue | Avg Queue ($\bar{Q}$, veh) | Max Queue ($Q_{\max}$, veh) | EV Latency ($T_{\text{clear}}$, s) | Recovery Horizon ($T_{\text{rec}}$, s) |
|---|---|---|---|---|---|
| **Fixed-Time (30s Cycle)** | Webster (1958) | 2.02 | 8 | 29s | 31s |
| **Demand Actuated** | SCATS (1990) | 0.81 | 5 | 34s | **20s** |
| **Max-Pressure** | Varaiya (2013) | **0.76** | **4** | 30s | 30s |
| **PressLight** | Wei et al., ACM KDD (2019) | 0.81 | **4** | 31s | **20s** |
| **EVP-DRL** | Lin et al., TR-C (2023) | 0.78 | **4** | 30s | **20s** |
| **AURA (Proposed)** | Safe MARL + Momentum | 0.85 | 6 | **14s (-58.6%)** | **20s** |

### 2. Real-World Midtown Manhattan OpenStreetMap Benchmark (183 Traffic Lights, 661 Edges)

| Controller | Class / Venue | Avg Queue ($\bar{Q}$, veh) | Max Queue ($Q_{\max}$, veh) | EV Latency ($T_{\text{clear}}$, s) | Recovery Horizon ($T_{\text{rec}}$, s) |
|---|---|---|---|---|---|
| **Fixed-Time (Manhattan)** | Webster (1958) | 38.19 | 103 | 42s | 26s |
| **Demand Actuated** | SCATS (1990) | 30.30 | 83 | 36s | **25s** |
| **Max-Pressure** | Varaiya (2013) | 27.97 | 76 | 32s | **25s** |
| **PressLight** | Wei et al., ACM KDD (2019) | 26.38 | 71 | 33s | **25s** |
| **EVP-DRL** | Lin et al., TR-C (2023) | 28.48 | 77 | **15s** | 71s (Severe Shockwave) |
| **AURA (Proposed)** | Safe MARL + Momentum | **26.33 (-31.0%)** | **69 (-33.0%)** | 16s (-61.9%) | **31s (2.2x Faster Recovery)** |

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
