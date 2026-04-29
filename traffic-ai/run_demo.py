import os
import sys
import time
import requests
import numpy as np
import torch
import torch.nn as nn
import traci

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

# IMPORTANT: SET THIS TO YOUR WINDOWS IPv4
BACKEND_URL = "http://172.28.160.1:3000/api/traffic" 
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
model.load_state_dict(torch.load("traffic_rl_model_final.pth"))
model.eval()

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
    traci.start(["sumo-gui", "-c", "network_config.sumocfg", "--start"])
    print("🚦 Production Agent Live. Listening for React Overrides...")

    while traci.simulation.getMinExpectedNumber() > 0:
        state = get_state()
        
        # 1. Check Backend for Manual Overrides
        system_mode = "AI_OPTIMIZED"
        try:
            res = requests.get(BACKEND_URL, timeout=0.2).json()
            system_mode = res.get("systemMode", "AI_OPTIMIZED")
        except: pass

        # 2. Execute Overrides or AI Logic
        if system_mode == "EMERGENCY_NS":
            target_phase, green_duration, signal_text = 0, 10, "🚨 AMBULANCE OVERRIDE: N/S GREEN"
        elif system_mode == "EMERGENCY_EW":
            target_phase, green_duration, signal_text = 2, 10, "🚨 AMBULANCE OVERRIDE: E/W GREEN"
        elif system_mode == "POLICE_STOP":
            # Phase 4 = All Red (if standard mapping), otherwise force yellow
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, 1) 
            for _ in range(10): traci.simulationStep(); time.sleep(0.05)
            continue
        else:
            # Normal AI Execution
            with torch.no_grad():
                action = model(torch.FloatTensor(state).to(device)).argmax().item()
            target_phase = 0 if action in [0, 2] else 2
            waiting = state[0]+state[2] if target_phase == 0 else state[1]+state[3]
            green_duration = max(10, min(int(waiting * 2), 45))
            signal_text = f"AI Expert: {'NORTH/SOUTH' if target_phase == 0 else 'EAST/WEST'} Cleared"

        # Apply Light
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
        try: requests.post(BACKEND_URL, json=data, timeout=0.2)
        except: pass

    traci.close()

if __name__ == "__main__": run_demo()