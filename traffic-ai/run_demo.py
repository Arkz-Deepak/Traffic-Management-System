import os
import sys
import time
import requests
import numpy as np
import torch
import torch.nn as nn

# Ensure SUMO tools path is registered BEFORE importing traci
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    if tools not in sys.path:
        sys.path.append(tools)
else:
    # Fallback to standard Debian/Ubuntu location if not explicitly exported
    default_sumo_home = '/usr/share/sumo'
    if os.path.exists(default_sumo_home):
        os.environ['SUMO_HOME'] = default_sumo_home
        tools = os.path.join(default_sumo_home, 'tools')
        if tools not in sys.path:
            sys.path.append(tools)
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")

import traci

# Base directory for relative file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurable backend bridge endpoint (defaults to localhost:3000)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:3000/api/traffic")
LANE_IDS = ["top0A0", "right0A0", "bottom0A0", "left0A0"]
TRAFFIC_LIGHT_ID = "A0"

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
    print(f"✅ Loaded trained DQN weights from: {os.path.basename(model_path)} (device: {device})")
else:
    print("⚠️ No pre-trained weights found; initializing random DQN baseline.")

def get_state():
    return np.array([traci.edge.getLastStepHaltingNumber(l) for l in LANE_IDS], dtype=np.float32)

def set_yellow_transition(target_phase):
    current = traci.trafficlight.getPhase(TRAFFIC_LIGHT_ID)
    if current != target_phase and current in [0, 2]:
        traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, 1 if current == 0 else 3)
        for _ in range(3): 
            traci.simulationStep()
            time.sleep(0.05)

def run_demo():
    sumo_cfg = os.path.join(BASE_DIR, "network_config.sumocfg")
    use_gui = os.environ.get("SUMO_GUI", "1") == "1" and bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    sumo_binary = "sumo-gui" if use_gui else "sumo"

    cmd = [sumo_binary, "-c", sumo_cfg, "--start"]
    print(f"🚀 Starting SUMO with binary: {sumo_binary} (Config: {os.path.basename(sumo_cfg)})")
    traci.start(cmd)
    print(f"🚦 Production Agent Live. Connected to backend at {BACKEND_URL}")

    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            state = get_state()
            
            # 1. Check Backend for Manual Overrides
            system_mode = "AI_OPTIMIZED"
            try:
                res = requests.get(BACKEND_URL, timeout=0.2).json()
                system_mode = res.get("systemMode", "AI_OPTIMIZED")
            except Exception:
                pass

            # 2. Execute Overrides or AI Logic
            if system_mode == "EMERGENCY_NS":
                target_phase, green_duration, signal_text = 0, 10, "🚨 AMBULANCE OVERRIDE: N/S GREEN"
            elif system_mode == "EMERGENCY_EW":
                target_phase, green_duration, signal_text = 2, 10, "🚨 AMBULANCE OVERRIDE: E/W GREEN"
            elif system_mode == "POLICE_STOP":
                traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, 1) 
                for _ in range(10):
                    traci.simulationStep()
                    time.sleep(0.05)
                continue
            else:
                # Normal AI Execution
                with torch.no_grad():
                    action = model(torch.FloatTensor(state).to(device)).argmax().item()
                target_phase = 0 if action in [0, 2] else 2
                waiting = state[0] + state[2] if target_phase == 0 else state[1] + state[3]
                # Dynamic green duration (10s to 45s) based on waiting queue
                green_duration = max(10, min(int(waiting * 2), 45))
                signal_text = f"AI Expert: {'NORTH/SOUTH' if target_phase == 0 else 'EAST/WEST'} Cleared"

            # Apply Light with Yellow clearance
            set_yellow_transition(target_phase)
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, target_phase)
            
            for _ in range(green_duration):
                traci.simulationStep()
                time.sleep(0.02) 

            # 3. Push Data to Dashboard
            next_state = get_state()
            data = {
                "laneACount": int(next_state[0]), "laneBCount": int(next_state[1]),
                "laneCCount": int(next_state[2]), "laneDCount": int(next_state[3]),
                "activeSignal": signal_text, "isAiActive": (system_mode == "AI_OPTIMIZED")
            }
            try:
                requests.post(BACKEND_URL, json=data, timeout=0.2)
            except Exception:
                pass

    except KeyboardInterrupt:
        print("\n🛑 Simulation interrupted by user.")
    finally:
        try:
            traci.close()
        except Exception:
            pass
        print("🏁 Simulation closed cleanly.")

if __name__ == "__main__":
    run_demo()
