import os
import sys
import time
import requests
import numpy as np

# Ensure SUMO tools path is set BEFORE importing traci
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
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")

import traci

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:3000/api/traffic")

# 10-Intersection Grid Mapping: Dashboard IDs 0-9 to SUMO junction IDs
NODE_MAP = {
    0: 'A0', 1: 'B0', 2: 'C0', 3: 'D0', 4: 'E0',
    5: 'A1', 6: 'B1', 7: 'C1', 8: 'D1', 9: 'E1'
}
REV_NODE_MAP = {v: k for k, v in NODE_MAP.items()}

# Incoming Approach Edges for each junction
JUNCTION_EDGES = {
    'A0': {'NS': ['A1A0', 'bottom0A0'], 'EW': ['left0A0', 'B0A0']},
    'B0': {'NS': ['B1B0', 'bottom1B0'], 'EW': ['A0B0', 'C0B0']},
    'C0': {'NS': ['C1C0', 'bottom2C0'], 'EW': ['B0C0', 'D0C0']},
    'D0': {'NS': ['D1D0', 'bottom3D0'], 'EW': ['C0D0', 'E0D0']},
    'E0': {'NS': ['E1E0', 'bottom4E0'], 'EW': ['D0E0', 'right0E0']},
    'A1': {'NS': ['top0A1', 'A0A1'], 'EW': ['left1A1', 'B1A1']},
    'B1': {'NS': ['top1B1', 'B0B1'], 'EW': ['A1B1', 'C1B1']},
    'C1': {'NS': ['top2C1', 'C0C1'], 'EW': ['B1C1', 'D1C1']},
    'D1': {'NS': ['top3D1', 'D0D1'], 'EW': ['C1D1', 'E1D1']},
    'E1': {'NS': ['top4E1', 'E0E1'], 'EW': ['D1E1', 'right1E1']},
}

class IntersectionAgent:
    def __init__(self, j_id):
        self.id = j_id
        self.current_phase = 0  # 0=NS Green, 1=NS Yellow, 2=EW Green, 3=EW Yellow
        self.phase_timer = 0
        self.min_green = 10
        self.max_green = 45
        self.preempt_active = False

    def get_queues(self):
        edges = JUNCTION_EDGES[self.id]
        ns_q = sum(traci.edge.getLastStepHaltingNumber(e) for e in edges['NS'])
        ew_q = sum(traci.edge.getLastStepHaltingNumber(e) for e in edges['EW'])
        return ns_q, ew_q

    def step(self, force_corridor_phase=None):
        ns_q, ew_q = self.get_queues()

        # Check for emergency preemption override
        if force_corridor_phase is not None:
            target_phase = force_corridor_phase  # 0 for NS, 2 for EW
            self.preempt_active = True
        else:
            self.preempt_active = False
            # Decentralized Max-Pressure / Queue-clearing action selection
            target_phase = 0 if ns_q >= ew_q else 2

        # Safe transition logic
        if self.current_phase in [0, 2] and target_phase != self.current_phase:
            # Need yellow clearance transition
            if self.phase_timer >= self.min_green or self.preempt_active:
                yellow_phase = 1 if self.current_phase == 0 else 3
                traci.trafficlight.setPhase(self.id, yellow_phase)
                self.current_phase = yellow_phase
                self.phase_timer = 0
            else:
                self.phase_timer += 1
        elif self.current_phase in [1, 3]:
            # Yellow clearance duration: 3 steps
            if self.phase_timer >= 3:
                new_phase = 2 if self.current_phase == 1 else 0
                traci.trafficlight.setPhase(self.id, new_phase)
                self.current_phase = new_phase
                self.phase_timer = 0
            else:
                self.phase_timer += 1
        else:
            # Holding green
            self.phase_timer += 1

def run_marl_corridor():
    sumo_cfg = os.path.join(BASE_DIR, "marl_config.sumocfg")
    use_gui = os.environ.get("SUMO_GUI", "1") == "1" and bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    sumo_binary = "sumo-gui" if use_gui else "sumo"

    print("=" * 65)
    print("🚦 AURA PHASE 2: 10-INTERSECTION DECENTRALIZED MARL CORRIDOR")
    print(f"   Binary: {sumo_binary} | Config: {os.path.basename(sumo_cfg)}")
    print(f"   Backend Telemetry Bridge: {BACKEND_URL}")
    print("=" * 65)

    traci.start([sumo_binary, "-c", sumo_cfg, "--start"])
    
    # Initialize 10 decentralized agents
    agents = {j_id: IntersectionAgent(j_id) for j_id in NODE_MAP.values()}

    active_green_wave_corridor = set()
    step = 0

    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step += 1

            # 1. Inspect emergency vehicle status
            all_vehicles = traci.vehicle.getIDList()
            ev_active = 'vip_ambulance' in all_vehicles
            ev_edge = traci.vehicle.getRoadID('vip_ambulance') if ev_active else None

            # 2. Check Backend for Manual/Tactical Overrides
            emergency_route = None
            try:
                res = requests.get(BACKEND_URL, timeout=0.1).json()
                sys_mode = res.get("systemMode", "AI_OPTIMIZED")
                emergency_route = res.get("emergencyRoute", None)
            except Exception:
                sys_mode = "AI_OPTIMIZED"

            # 3. Dynamic Green Wave Calculation
            force_phases = {}
            if emergency_route and len(emergency_route) > 0:
                # User drew a path on the React Dashboard!
                target_junctions = [NODE_MAP[int(n)] for n in emergency_route if int(n) in NODE_MAP]
                for j in target_junctions:
                    force_phases[j] = 2  # Enforce Green Wave along arterial corridor
                
                # Dynamically spawn ambulance if not already in simulation
                if not getattr(run_marl_corridor, 'dispatched', False):
                    amb_id = f"ambulance_{step}"
                    try:
                        traci.vehicle.add(amb_id, 'corridor_row0', typeID='ambulance_type', departSpeed='max')
                        print(f"🚑 [DDS Dispatch] Live Green Wave triggered for route: {target_junctions} (Vehicle: {amb_id})")
                        run_marl_corridor.dispatched = True
                    except Exception:
                        pass
            elif ev_active and ev_edge:
                # If along Row 0: left0A0 -> A0B0 -> B0C0 -> C0D0 -> D0E0 -> E0right0
                if any(x in ev_edge for x in ['A0', 'B0', 'C0', 'D0', 'E0']):
                    for j in ['A0', 'B0', 'C0', 'D0', 'E0']:
                        force_phases[j] = 2  # EW Green along the arterial highway
                elif any(x in ev_edge for x in ['A1', 'B1', 'C1', 'D1', 'E1']):
                    for j in ['A1', 'B1', 'C1', 'D1', 'E1']:
                        force_phases[j] = 2  # EW Green along top arterial highway
            elif sys_mode == "EMERGENCY_NS":
                for j in NODE_MAP.values(): force_phases[j] = 0
            elif sys_mode == "EMERGENCY_EW":
                for j in NODE_MAP.values(): force_phases[j] = 2

            # 4. Step each of the 10 decentralized agents
            total_grid_queues = []
            for j_id, agent in agents.items():
                target_override = force_phases.get(j_id, None)
                agent.step(target_override)
                ns_q, ew_q = agent.get_queues()
                total_grid_queues.append(ns_q + ew_q)

            # 5. Broadcast live telemetry to Dashboard every 5 simulation steps
            if step % 5 == 0:
                sample_j = agents['A0']
                ns_q, ew_q = sample_j.get_queues()
                
                status_text = "MARL: Grid Equilibrium"
                if ev_active:
                    status_text = f"🚑 GREEN WAVE ACTIVE: Corridor Cleared ({ev_edge})"
                elif sys_mode != "AI_OPTIMIZED":
                    status_text = f"🚨 MANUAL OVERRIDE: {sys_mode}"

                telemetry = {
                    "laneACount": int(ns_q // 2),
                    "laneBCount": int(ew_q // 2),
                    "laneCCount": int(ns_q - (ns_q // 2)),
                    "laneDCount": int(ew_q - (ew_q // 2)),
                    "activeSignal": status_text,
                    "isAiActive": True,
                    "gridTotalQueue": int(sum(total_grid_queues))
                }
                try:
                    requests.post(BACKEND_URL, json=telemetry, timeout=0.1)
                except Exception:
                    pass

            time.sleep(0.015)  # Visual smoothing

    except KeyboardInterrupt:
        print("\n🛑 MARL simulation interrupted by user.")
    finally:
        try:
            traci.close()
        except Exception:
            pass
        print("🏁 Simulation closed cleanly.")

if __name__ == "__main__":
    run_marl_corridor()
