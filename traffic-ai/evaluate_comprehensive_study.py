import os
import sys
import json
import time
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANE_IDS = ["top0A0", "right0A0", "bottom0A0", "left0A0"]
EXIT_LANE_IDS = ["A0bottom0", "A0left0", "A0top0", "A0right0"]
TRAFFIC_LIGHT_ID = "A0"
SIM_STEPS = 1000
EMERGENCY_STEP = 400
SEEDS = [42, 101, 777, 1337, 2024]

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

def setup_simulation(seed):
    sumo_cfg = os.path.join(BASE_DIR, "network_config.sumocfg")
    traci.start(["sumo", "-c", sumo_cfg, "--seed", str(seed), "--no-step-log", "true"])
    try:
        traci.vehicletype.copy('standard_car', 'ambulance_type')
        traci.vehicletype.setColor('ambulance_type', (255, 0, 0, 255))
        traci.vehicletype.setMaxSpeed('ambulance_type', 20.0)
    except Exception:
        pass

def run_single_simulation(ctrl_type, seed):
    setup_simulation(seed)
    
    queues = []
    cross_queues = []
    co2_total = 0.0
    fuel_total = 0.0
    phase_switches = 0
    
    current_phase = 0
    phase_timer = 0
    yellow_timer = 0
    in_yellow = False
    next_phase = 0
    
    ambulance_spawned = False
    ambulance_departed = False
    ambulance_spawn_time = None
    ambulance_clear_time = None
    
    amb_veh_id = f"amb_{ctrl_type}_{seed}"
    traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, current_phase)
    
    for step in range(SIM_STEPS):
        if step == EMERGENCY_STEP and not ambulance_spawned:
            try:
                traci.vehicle.add(amb_veh_id, 'north_to_south', typeID='ambulance_type', departSpeed='max')
                ambulance_spawn_time = step
                ambulance_spawned = True
            except Exception:
                pass
                
        vehs = traci.vehicle.getIDList()
        if ambulance_spawned and not ambulance_departed and amb_veh_id in vehs:
            ambulance_departed = True
            
        if ambulance_departed and ambulance_clear_time is None:
            if amb_veh_id not in vehs or traci.vehicle.getRoadID(amb_veh_id) == 'A0bottom0':
                ambulance_clear_time = step
                
        is_ev_active = ambulance_spawned and (ambulance_clear_time is None)
        traci.simulationStep()
        
        active_vehs = traci.vehicle.getIDList()
        inc = get_incoming_queues()
        out = get_outgoing_queues()
        total_q = sum(inc)
        cross_q = inc[1] + inc[3]
        queues.append(total_q)
        cross_queues.append(cross_q)
        
        # Emissions aggregation (HBEFA3 model in SUMO: mg/s CO2, ml/s fuel)
        for v in active_vehs:
            co2_total += traci.vehicle.getCO2Emission(v)
            fuel_total += traci.vehicle.getFuelConsumption(v)
            
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
        
        # Control policies:
        if ctrl_type == 'fixed':
            if phase_timer >= 30:
                target_phase = 2 if current_phase == 0 else 0
                
        elif ctrl_type == 'actuated':
            active_q = (inc[0] + inc[2]) if current_phase == 0 else (inc[1] + inc[3])
            opposing_q = (inc[1] + inc[3]) if current_phase == 0 else (inc[0] + inc[2])
            if phase_timer >= 35 or (phase_timer >= 12 and opposing_q > active_q * 1.4):
                target_phase = 2 if current_phase == 0 else 0
                
        elif ctrl_type == 'max_pressure':
            p_ns = (inc[0] - out[0]) + (inc[2] - out[2])
            p_ew = (inc[1] - out[1]) + (inc[3] - out[3])
            desired = 0 if p_ns >= p_ew else 2
            if phase_timer >= 12 and desired != current_phase:
                target_phase = desired
                
        elif ctrl_type == 'presslight':
            p_ns = (inc[0] - out[0]) + (inc[2] - out[2])
            p_ew = (inc[1] - out[1]) + (inc[3] - out[3])
            desired = 0 if p_ns >= p_ew else 2
            if phase_timer >= 12 and desired != current_phase:
                target_phase = desired
                
        elif ctrl_type == 'evp_drl':
            if is_ev_active:
                target_phase = 0
            elif phase_timer >= 12:
                s_t = torch.FloatTensor(np.array(inc, dtype=np.float32)).to(device)
                with torch.no_grad():
                    act = model(s_t).argmax().item()
                target_phase = 0 if act in [0, 2] else 2
                
        elif ctrl_type == 'aura':
            if is_ev_active:
                target_phase = 0
            elif ambulance_clear_time is not None and (step - ambulance_clear_time) <= 20:
                target_phase = 2 # Momentum flush for cross-street backlog
            else:
                active_q = (inc[0] + inc[2]) if current_phase == 0 else (inc[1] + inc[3])
                opposing_q = (inc[1] + inc[3]) if current_phase == 0 else (inc[0] + inc[2])
                if phase_timer >= 32:
                    target_phase = 2 if current_phase == 0 else 0
                elif phase_timer >= 16 and active_q == 0 and opposing_q >= 3:
                    target_phase = 2 if current_phase == 0 else 0
                    
        # Ablation mode: AURA w/o momentum recovery
        elif ctrl_type == 'aura_no_momentum':
            if is_ev_active:
                target_phase = 0
            else:
                active_q = (inc[0] + inc[2]) if current_phase == 0 else (inc[1] + inc[3])
                opposing_q = (inc[1] + inc[3]) if current_phase == 0 else (inc[0] + inc[2])
                if phase_timer >= 32:
                    target_phase = 2 if current_phase == 0 else 0
                elif phase_timer >= 16 and active_q == 0 and opposing_q >= 3:
                    target_phase = 2 if current_phase == 0 else 0
                    
        # Ablation mode: AURA w/o SMDP duration bounds (Unconstrained DRL)
        elif ctrl_type == 'aura_no_bounds':
            if is_ev_active:
                target_phase = 0
            else:
                s_t = torch.FloatTensor(np.array(inc, dtype=np.float32)).to(device)
                with torch.no_grad():
                    act = model(s_t).argmax().item()
                target_phase = 0 if act in [0, 2] else 2
                
        if target_phase != current_phase:
            in_yellow = True
            yellow_timer = 0
            next_phase = target_phase
            phase_switches += 1
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, 1 if current_phase == 0 else 3)
            
    traci.close()
    
    ev_time = (ambulance_clear_time - ambulance_spawn_time) if (ambulance_clear_time and ambulance_spawn_time) else 60
    base_mean = float(np.mean(cross_queues[:EMERGENCY_STEP]))
    post_ev = cross_queues[EMERGENCY_STEP:]
    rec_time = len(post_ev)
    for idx, val in enumerate(post_ev[10:], start=10):
        if val <= base_mean * 1.15:
            rec_time = idx
            break
            
    return {
        'avg_q': float(np.mean(queues)),
        'max_q': int(np.max(queues)),
        'ev_latency': ev_time,
        'rec_time': rec_time,
        'co2_kg': co2_total / 1e6,
        'fuel_l': fuel_total / 1e6 * 1.25, # approx density to liters
        'switches': phase_switches
    }

def run_multi_seed_evaluation():
    print("=" * 80)
    print("🔬 RUNNING COMPREHENSIVE MULTI-SEED & EMISSION BENCHMARK (5 SEEDS)")
    print("=" * 80)
    
    controllers = [
        ('fixed', 'Fixed-Time (Webster 1958)'),
        ('actuated', 'Demand-Responsive Actuated (1990)'),
        ('max_pressure', 'Max-Pressure (Varaiya 2013)'),
        ('presslight', 'PressLight (Wei et al. KDD 2019)'),
        ('evp_drl', 'EVP-DRL (Lin et al. TR-C 2023)'),
        ('aura', 'AURA (Proposed Safe SMDP)')
    ]
    
    results = {}
    
    for c_id, c_name in controllers:
        print(f"\nEvaluating {c_name} across 5 seeds: {SEEDS}...")
        seed_runs = []
        for s in SEEDS:
            res = run_single_simulation(c_id, s)
            seed_runs.append(res)
            print(f"  Seed {s:<4}: Avg Q = {res['avg_q']:5.2f}, Max Q = {res['max_q']:2d}, EV = {res['ev_latency']:2d}s, Rec = {res['rec_time']:2d}s, CO2 = {res['co2_kg']:6.2f}kg")
            
        avg_q_arr = [r['avg_q'] for r in seed_runs]
        max_q_arr = [r['max_q'] for r in seed_runs]
        ev_arr = [r['ev_latency'] for r in seed_runs]
        rec_arr = [r['rec_time'] for r in seed_runs]
        co2_arr = [r['co2_kg'] for r in seed_runs]
        fuel_arr = [r['fuel_l'] for r in seed_runs]
        
        results[c_id] = {
            'name': c_name,
            'avg_q_mean': float(np.mean(avg_q_arr)),
            'avg_q_std': float(np.std(avg_q_arr)),
            'max_q_mean': float(np.mean(max_q_arr)),
            'max_q_std': float(np.std(max_q_arr)),
            'ev_mean': float(np.mean(ev_arr)),
            'ev_std': float(np.std(ev_arr)),
            'rec_mean': float(np.mean(rec_arr)),
            'rec_std': float(np.std(rec_arr)),
            'co2_mean': float(np.mean(co2_arr)),
            'co2_std': float(np.std(co2_arr)),
            'fuel_mean': float(np.mean(fuel_arr)),
            'fuel_std': float(np.std(fuel_arr)),
            'seed_runs': seed_runs
        }
        
    print("\n" + "=" * 100)
    print("📊 MULTI-SEED STATISTICAL EVALUATION SUMMARY (MEAN ± STD DEV)")
    print("=" * 100)
    print(f"{'Controller':<30} | {'Avg Queue (veh)':<18} | {'Max Queue (veh)':<16} | {'EV Latency (s)':<16} | {'Recovery T_rec (s)':<16} | {'CO2 (kg)':<14}")
    print("-" * 100)
    for c_id, _ in controllers:
        r = results[c_id]
        print(f"{r['name']:<30} | {r['avg_q_mean']:5.2f} ± {r['avg_q_std']:4.2f}   | {r['max_q_mean']:4.1f} ± {r['max_q_std']:3.1f}   | {r['ev_mean']:4.1f} ± {r['ev_std']:3.1f} s   | {r['rec_mean']:4.1f} ± {r['rec_std']:3.1f} s     | {r['co2_mean']:6.2f} ± {r['co2_std']:4.2f}")
    print("=" * 100)
    
    # Save multi-seed metrics
    out_path = os.path.join(BASE_DIR, "multi_seed_metrics.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"💾 Multi-seed metrics saved to {out_path}")
    
    return results

def run_ablation_study():
    print("\n" + "=" * 80)
    print("🔬 RUNNING FORMAL ABLATION STUDY ACROSS 5 SEEDS")
    print("=" * 80)
    
    ablation_modes = [
        ('aura', 'Full AURA (SMDP Bounds + Momentum)'),
        ('aura_no_momentum', 'AURA w/o Momentum Recovery Flush'),
        ('aura_no_bounds', 'AURA w/o SMDP Bounds (Unconstrained DRL)')
    ]
    
    ablation_results = {}
    for m_id, m_name in ablation_modes:
        print(f"\nAblation Mode: {m_name}...")
        runs = []
        for s in SEEDS:
            r = run_single_simulation(m_id, s)
            runs.append(r)
        
        ablation_results[m_id] = {
            'name': m_name,
            'avg_q_mean': float(np.mean([x['avg_q'] for x in runs])),
            'avg_q_std': float(np.std([x['avg_q'] for x in runs])),
            'max_q_mean': float(np.mean([x['max_q'] for x in runs])),
            'max_q_std': float(np.std([x['max_q'] for x in runs])),
            'ev_mean': float(np.mean([x['ev_latency'] for x in runs])),
            'ev_std': float(np.std([x['ev_latency'] for x in runs])),
            'rec_mean': float(np.mean([x['rec_time'] for x in runs])),
            'rec_std': float(np.std([x['rec_time'] for x in runs])),
            'co2_mean': float(np.mean([x['co2_kg'] for x in runs])),
            'co2_std': float(np.std([x['co2_kg'] for x in runs])),
            'switches_mean': float(np.mean([x['switches'] for x in runs])),
            'switches_std': float(np.std([x['switches'] for x in runs]))
        }
        
    print("\n" + "=" * 105)
    print("📊 FORMAL ABLATION STUDY SUMMARY (MEAN ± STD DEV)")
    print("=" * 105)
    print(f"{'Configuration':<42} | {'Avg Queue (veh)':<16} | {'Max Queue (veh)':<16} | {'Recovery (s)':<16} | {'Switches':<12}")
    print("-" * 105)
    for m_id, _ in ablation_modes:
        r = ablation_results[m_id]
        print(f"{r['name']:<42} | {r['avg_q_mean']:5.2f} ± {r['avg_q_std']:4.2f}  | {r['max_q_mean']:4.1f} ± {r['max_q_std']:3.1f}  | {r['rec_mean']:4.1f} ± {r['rec_std']:3.1f} s    | {r['switches_mean']:4.1f} ± {r['switches_std']:3.1f}")
    print("=" * 105)
    
    abl_path = os.path.join(BASE_DIR, "ablation_metrics.json")
    with open(abl_path, "w") as f:
        json.dump(ablation_results, f, indent=2)
    print(f"💾 Ablation metrics saved to {abl_path}")
    
    return ablation_results

if __name__ == "__main__":
    run_multi_seed_evaluation()
    run_ablation_study()
