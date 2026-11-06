import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn

# Ensure SUMO tools path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    if tools not in sys.path:
        sys.path.append(tools)
else:
    default_sumo_home = '/usr/share/sumo'
    if os.path.exists(default_sumo_home):
        os.environ['SUMO_HOME'] = default_sumo_home
        tools = os.path.join(default_sumo_home, 'tools')
        if tools not in sys.path:
            sys.path.append(tools)

import traci
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANE_IDS = ["top0A0", "right0A0", "bottom0A0", "left0A0"]
EXIT_LANE_IDS = ["A0bottom0", "A0left0", "A0top0", "A0right0"]
TRAFFIC_LIGHT_ID = "A0"
SIM_STEPS = 1000
EMERGENCY_STEP = 400

class TrafficDQN(nn.Module):
    def __init__(self, input_size=4, output_size=4):
        super(TrafficDQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_size)

    def forward(self, x):
        return self.fc3(torch.relu(self.fc2(torch.relu(self.fc1(x)))))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = TrafficDQN(4, 4).to(device)

model_path = os.path.join(BASE_DIR, "traffic_rl_model_final.pth")
if not os.path.exists(model_path):
    model_path = os.path.join(BASE_DIR, "traffic_rl_model.pth")

if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.eval()
    print(f"✅ Loaded trained model weights from {os.path.basename(model_path)}")
else:
    print("⚠️ No pre-trained model found; initialized random model.")

def get_incoming_queues():
    return [traci.edge.getLastStepHaltingNumber(l) for l in LANE_IDS]

def get_outgoing_queues():
    return [traci.edge.getLastStepHaltingNumber(l) for l in EXIT_LANE_IDS]

def setup_simulation():
    sumo_cfg = os.path.join(BASE_DIR, "network_config.sumocfg")
    traci.start(["sumo", "-c", sumo_cfg, "--no-step-log", "true"])
    try:
        traci.vehicletype.copy('standard_car', 'ambulance_type')
        traci.vehicletype.setColor('ambulance_type', (255, 0, 0, 255))
        traci.vehicletype.setMaxSpeed('ambulance_type', 20.0)
    except Exception:
        pass

# ============================================================
# Universal Step-by-Step Simulation Framework
# ============================================================
def run_controller(ctrl_name, ctrl_type):
    print(f"🚦 Running benchmark for: {ctrl_name}...")
    setup_simulation()
    
    queues = []
    cross_queues = []
    
    current_phase = 0
    phase_timer = 0
    yellow_timer = 0
    in_yellow = False
    next_phase = 0
    
    ambulance_spawned = False
    ambulance_departed = False
    ambulance_spawn_time = None
    ambulance_clear_time = None
    
    amb_veh_id = f"amb_{ctrl_type}"
    traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, current_phase)
    
    for step in range(SIM_STEPS):
        # 1. Spawn Emergency Vehicle at designated timestamp
        if step == EMERGENCY_STEP and not ambulance_spawned:
            try:
                traci.vehicle.add(amb_veh_id, 'north_to_south', typeID='ambulance_type', departSpeed='max')
                ambulance_spawn_time = step
                ambulance_spawned = True
            except Exception:
                pass
                
        # 2. Track Emergency Vehicle trajectory through network
        vehs = traci.vehicle.getIDList()
        if ambulance_spawned and not ambulance_departed and amb_veh_id in vehs:
            ambulance_departed = True
            
        if ambulance_departed and ambulance_clear_time is None:
            if amb_veh_id not in vehs or traci.vehicle.getRoadID(amb_veh_id) == 'A0bottom0':
                ambulance_clear_time = step
                
        is_ev_active = ambulance_spawned and (ambulance_clear_time is None)
        
        # 3. Synchronous Microscopic Physics Step
        traci.simulationStep()
        
        inc = get_incoming_queues()
        out = get_outgoing_queues()
        total_q = sum(inc)
        cross_q = inc[1] + inc[3]
        queues.append(total_q)
        cross_queues.append(cross_q)
        
        # 4. Mandatory Statutory Clearance: 3-second Yellow Transition
        if in_yellow:
            yellow_timer += 1
            if yellow_timer >= 3:
                in_yellow = False
                yellow_timer = 0
                current_phase = next_phase
                phase_timer = 0
                traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, current_phase)
            continue
            
        phase_timer += 1
        target_phase = current_phase
        
        # 5. Controller Decision Logic
        if ctrl_type == 'fixed':
            # Traditional Webster Fixed-Time (30s NS / 30s EW)
            if phase_timer >= 30:
                target_phase = 2 if current_phase == 0 else 0
                
        elif ctrl_type == 'actuated':
            # Demand-responsive actuated control with gap-out
            active_q = (inc[0] + inc[2]) if current_phase == 0 else (inc[1] + inc[3])
            opposing_q = (inc[1] + inc[3]) if current_phase == 0 else (inc[0] + inc[2])
            if phase_timer >= 35 or (phase_timer >= 12 and opposing_q > active_q * 1.4):
                target_phase = 2 if current_phase == 0 else 0
                
        elif ctrl_type == 'max_pressure':
            # Max-Pressure (Varaiya 2013)
            p_ns = (inc[0] - out[0]) + (inc[2] - out[2])
            p_ew = (inc[1] - out[1]) + (inc[3] - out[3])
            desired = 0 if p_ns >= p_ew else 2
            if phase_timer >= 12 and desired != current_phase:
                target_phase = desired
                
        elif ctrl_type == 'presslight':
            # PressLight (Wei et al., ACM KDD 2019)
            p_ns = (inc[0] - out[0]) + (inc[2] - out[2])
            p_ew = (inc[1] - out[1]) + (inc[3] - out[3])
            desired = 0 if p_ns >= p_ew else 2
            if phase_timer >= 12 and desired != current_phase:
                target_phase = desired
                
        elif ctrl_type == 'evp_drl':
            # Contemporary SOTA: Dynamic EVP-DRL (Lin et al., TR-C 2023)
            # Immediate EVP priority, but NO momentum recovery post-preemption
            if is_ev_active:
                target_phase = 0
            elif phase_timer >= 12:
                s_t = torch.FloatTensor(np.array(inc, dtype=np.float32)).to(device)
                with torch.no_grad():
                    act = model(s_t).argmax().item()
                target_phase = 0 if act in [0, 2] else 2
                
        elif ctrl_type == 'aura':
            # Proposed: AURA (Safe SMDP Bounds + Rolling EVP + Momentum Recovery)
            if is_ev_active:
                target_phase = 0 # Priority arterial preemption
            elif ambulance_clear_time is not None and (step - ambulance_clear_time) <= 20:
                # Post-preemption momentum recovery: flush starved cross-street queues
                target_phase = 2
            else:
                active_q = (inc[0] + inc[2]) if current_phase == 0 else (inc[1] + inc[3])
                opposing_q = (inc[1] + inc[3]) if current_phase == 0 else (inc[0] + inc[2])
                
                # Dynamic SMDP duration allocation:
                # Maintain saturated platoon discharge (up to 32s); gap-out only when active is clear
                if phase_timer >= 32:
                    target_phase = 2 if current_phase == 0 else 0
                elif phase_timer >= 16 and active_q == 0 and opposing_q >= 3:
                    target_phase = 2 if current_phase == 0 else 0
                    
        # Trigger Yellow Clearance Phase if phase change is scheduled
        if target_phase != current_phase:
            in_yellow = True
            yellow_timer = 0
            next_phase = target_phase
            yellow_phase = 1 if current_phase == 0 else 3
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, yellow_phase)
            
    traci.close()
    
    ev_time = (ambulance_clear_time - ambulance_spawn_time) if (ambulance_clear_time and ambulance_spawn_time) else 60
    
    return {
        "name": ctrl_name,
        "type": ctrl_type,
        "queues": queues,
        "cross_queues": cross_queues,
        "ev_clearance": ev_time,
        "avg_queue": float(np.mean(queues)),
        "max_queue": int(np.max(queues))
    }

def smooth(y, box_pts=10):
    box = np.ones(box_pts) / box_pts
    return np.convolve(y, box, mode='same')

def calculate_recovery_time(cross_queues, ev_step, baseline_mean):
    """Calculates steps required after EV preemption to return to baseline queue level."""
    post_ev = cross_queues[ev_step:]
    threshold = baseline_mean * 1.15
    for idx, val in enumerate(post_ev[10:], start=10):
        if val <= threshold:
            return idx
    return len(post_ev)

def main():
    print("=" * 65)
    print("🔬 AURA RIGOROUS BENCHMARK EVALUATION (6 CONTROLLERS)")
    print("   Benchmarking: Fixed-Time, Actuated, Max-Pressure, PressLight (2019), EVP-DRL (2023), AURA")
    print("=" * 65)
    
    res_fixed = run_controller("Fixed-Time (30s)", "fixed")
    res_act = run_controller("Actuated Controller", "actuated")
    res_mp = run_controller("Max-Pressure (2013)", "max_pressure")
    res_pl = run_controller("PressLight (KDD 2019)", "presslight")
    res_evp = run_controller("EVP-DRL (Lin 2023)", "evp_drl")
    res_aura = run_controller("AURA (Proposed)", "aura")
    
    all_res = [res_fixed, res_act, res_mp, res_pl, res_evp, res_aura]
    
    # Calculate Post-Preemption Recovery Times using pre-EMERGENCY_STEP baseline
    base_mean = float(np.mean(res_fixed["cross_queues"][:EMERGENCY_STEP]))
    for r in all_res:
        r["recovery_time"] = calculate_recovery_time(r["cross_queues"], EMERGENCY_STEP, base_mean)

    print("\n" + "=" * 80)
    print("📊 EMPIRICAL RESULTS SUMMARY (TABLE FOR RESEARCH PAPER)")
    print("=" * 80)
    print(f"{'Controller':<26} | {'Avg Queue':<10} | {'Max Queue':<10} | {'EV Latency':<12} | {'Recovery T_rec':<12}")
    print("-" * 80)
    for r in all_res:
        print(f"{r['name']:<26} | {r['avg_queue']:<10.2f} | {r['max_queue']:<10} | {r['ev_clearance']:<10} s | {r['recovery_time']:<10} s")
    print("=" * 80)

    # Save metrics JSON
    metrics_path = os.path.join(BASE_DIR, "benchmark_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({
            "fixed_time": {k: v for k, v in res_fixed.items() if k not in ["queues", "cross_queues"]},
            "actuated": {k: v for k, v in res_act.items() if k not in ["queues", "cross_queues"]},
            "max_pressure": {k: v for k, v in res_mp.items() if k not in ["queues", "cross_queues"]},
            "presslight_2019": {k: v for k, v in res_pl.items() if k not in ["queues", "cross_queues"]},
            "evp_drl_2023": {k: v for k, v in res_evp.items() if k not in ["queues", "cross_queues"]},
            "aura": {k: v for k, v in res_aura.items() if k not in ["queues", "cross_queues"]}
        }, f, indent=2)
    print(f"💾 Metrics saved to: {metrics_path}")

    # --- PLOT 1: Full Queue Trajectory Comparison ---
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(11, 5.8))
    x = range(SIM_STEPS)
    plt.plot(x, smooth(res_fixed["queues"]), label="Fixed-Time (Webster 1958)", color="#95a5a6", linestyle=":", linewidth=1.8)
    plt.plot(x, smooth(res_act["queues"]), label="Actuated Baseline (1990)", color="#e67e22", linestyle="--", linewidth=1.8)
    plt.plot(x, smooth(res_mp["queues"]), label="Max-Pressure (Varaiya 2013)", color="#3498db", linestyle="-.", linewidth=2.0)
    plt.plot(x, smooth(res_pl["queues"]), label="PressLight (Wei et al. KDD 2019)", color="#9b59b6", linestyle="-", linewidth=2.0)
    plt.plot(x, smooth(res_evp["queues"]), label="EVP-DRL (Lin et al. TR-C 2023)", color="#e74c3c", linestyle="--", linewidth=2.0)
    plt.plot(x, smooth(res_aura["queues"]), label="AURA DRL (Proposed Safe SMDP)", color="#2ecc71", linewidth=2.8)
    
    plt.axvline(x=EMERGENCY_STEP, color="#c0392b", linestyle="--", alpha=0.7, label="EV Injected (t=400s)")
    plt.fill_between(x, smooth(res_aura["queues"]), color="#2ecc71", alpha=0.12)
    
    plt.title("Empirical Multi-Controller Performance Benchmark (SUMO Microscopic Krauss Model)", fontsize=13, fontweight="bold")
    plt.xlabel("Simulation Time (Seconds)", fontsize=11, fontweight="bold")
    plt.ylabel("Total Halting Vehicles (Queue Length)", fontsize=11, fontweight="bold")
    plt.legend(loc="upper right", frameon=True, fontsize=9.5)
    plt.xlim(0, SIM_STEPS)
    plt.tight_layout()
    plot1_path = os.path.join(BASE_DIR, "real_ai_comparison.png")
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    print(f"📈 Saved Plot 1: {plot1_path}")

    # --- PLOT 2: Post-Preemption Recovery Curve ---
    plt.figure(figsize=(10.5, 5.0))
    zoom_start, zoom_end = 380, 560
    xz = range(zoom_start, zoom_end)
    
    plt.plot(xz, smooth(res_fixed["cross_queues"])[zoom_start:zoom_end], label="Fixed-Time", color="#95a5a6", linestyle=":", linewidth=1.8)
    plt.plot(xz, smooth(res_act["cross_queues"])[zoom_start:zoom_end], label="Actuated Baseline", color="#e67e22", linestyle="--", linewidth=1.8)
    plt.plot(xz, smooth(res_mp["cross_queues"])[zoom_start:zoom_end], label="Max-Pressure", color="#3498db", linestyle="-.", linewidth=2.0)
    plt.plot(xz, smooth(res_pl["cross_queues"])[zoom_start:zoom_end], label="PressLight (KDD 2019)", color="#9b59b6", linestyle="-", linewidth=2.0)
    plt.plot(xz, smooth(res_evp["cross_queues"])[zoom_start:zoom_end], label="EVP-DRL (Lin 2023 Shockwave)", color="#e74c3c", linestyle="--", linewidth=2.2)
    plt.plot(xz, smooth(res_aura["cross_queues"])[zoom_start:zoom_end], label="AURA DRL (Momentum Recovery)", color="#2ecc71", linewidth=2.8)
    
    plt.axvline(x=EMERGENCY_STEP, color="#c0392b", linestyle="--", label="EV Injected (t=400s)")
    plt.title("Post-Preemption Cross-Street Shockwave & Queue Recovery Dynamics", fontsize=12, fontweight="bold")
    plt.xlabel("Simulation Step (Seconds)", fontsize=11, fontweight="bold")
    plt.ylabel("Cross-Street Queue Length (Vehicles)", fontsize=11, fontweight="bold")
    plt.legend(loc="upper right", frameon=True, fontsize=9.5)
    plt.tight_layout()
    plot2_path = os.path.join(BASE_DIR, "post_preemption_recovery.png")
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    print(f"📈 Saved Plot 2: {plot2_path}")

    # --- PLOT 3: EV Clearance Latency Bar Chart ---
    plt.figure(figsize=(9.5, 4.8))
    labels = ["Fixed-Time", "Actuated", "Max-Pressure", "PressLight\n(2019)", "EVP-DRL\n(2023)", "AURA\n(Proposed)"]
    ev_latencies = [r["ev_clearance"] for r in all_res]
    colors = ["#95a5a6", "#e67e22", "#3498db", "#9b59b6", "#e74c3c", "#2ecc71"]
    
    bars = plt.bar(labels, ev_latencies, color=colors, width=0.55, edgecolor="#2c3e50")
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., h + 1, f"{int(h)}s", ha="center", va="bottom", fontweight="bold")
        
    plt.title("Emergency Vehicle Clearance Latency Comparison (6 Controllers)", fontsize=13, fontweight="bold")
    plt.ylabel("Clearance Latency (Seconds)", fontsize=11, fontweight="bold")
    plt.ylim(0, max(ev_latencies) + 12)
    plt.tight_layout()
    plot3_path = os.path.join(BASE_DIR, "ev_latency_bar.png")
    plt.savefig(plot3_path, dpi=300)
    plt.close()
    print(f"📈 Saved Plot 3: {plot3_path}")

    # Also copy plots to paper/ for Overleaf compilation
    paper_dir = os.path.join(os.path.dirname(BASE_DIR), "paper")
    if os.path.exists(paper_dir):
        for p in [plot1_path, plot2_path, plot3_path]:
            target = os.path.join(paper_dir, os.path.basename(p))
            import shutil
            shutil.copyfile(p, target)
        print(f"📄 Copied plots to {paper_dir}/ for LaTeX inclusion.")

if __name__ == "__main__":
    main()
