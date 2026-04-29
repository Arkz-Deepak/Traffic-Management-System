import os
import sys
import numpy as np
import torch
import torch.nn as nn
import traci
import matplotlib.pyplot as plt

# Ensure SUMO is linked
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

LANE_IDS = ["top0A0", "right0A0", "bottom0A0", "left0A0"]
TRAFFIC_LIGHT_ID = "A0"
SIM_STEPS = 1000  # We will test both models over 1,000 seconds of traffic

# --- Load the AI Brain ---
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
    return [traci.edge.getLastStepHaltingNumber(l) for l in LANE_IDS]

def get_total_queue():
    return sum(get_state())

# --- Test 1: The "Dumb" Fixed Time Controller ---
def evaluate_fixed_time():
    print("🚦 Running baseline Fixed-Time simulation (30s phases)...")
    traci.start(["sumo", "-c", "network_config.sumocfg", "--no-step-log", "true"])
    
    queue_history = []
    # Standard 4-phase cycle: 30s Green NS, 3s Yellow, 30s Green EW, 3s Yellow
    phases = [(0, 30), (1, 3), (2, 30), (3, 3)] 
    current_phase_idx = 0
    phase_timer = 0
    
    traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, phases[current_phase_idx][0])
    
    for step in range(SIM_STEPS):
        if phase_timer >= phases[current_phase_idx][1]:
            current_phase_idx = (current_phase_idx + 1) % 4
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, phases[current_phase_idx][0])
            phase_timer = 0
            
        traci.simulationStep()
        queue_history.append(get_total_queue())
        phase_timer += 1
        
    traci.close()
    return queue_history

# --- Test 2: Your Trained RL Agent ---
def evaluate_ai_model():
    print("🧠 Running VisionX AI Model simulation...")
    traci.start(["sumo", "-c", "network_config.sumocfg", "--no-step-log", "true"])
    
    queue_history = []
    step = 0
    
    while step < SIM_STEPS:
        state = get_state()
        state_tensor = torch.FloatTensor(np.array(state)).to(device)
        
        with torch.no_grad():
            action = model(state_tensor).argmax().item()
            
        target_phase = 0 if action in [0, 2] else 2
        current_phase = traci.trafficlight.getPhase(TRAFFIC_LIGHT_ID)
        
        # 3s Yellow transition
        if current_phase != target_phase and current_phase in [0, 2]:
            yellow_phase = 1 if current_phase == 0 else 3
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, yellow_phase)
            for _ in range(3):
                if step >= SIM_STEPS: break
                traci.simulationStep()
                queue_history.append(get_total_queue())
                step += 1
                
        if step >= SIM_STEPS: break
        
        # Apply Green Phase dynamically
        traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, target_phase)
        waiting = state[0]+state[2] if target_phase == 0 else state[1]+state[3]
        green_duration = max(10, min(int(waiting * 2), 45))
        
        for _ in range(green_duration):
            if step >= SIM_STEPS: break
            traci.simulationStep()
            queue_history.append(get_total_queue())
            step += 1
            
    traci.close()
    return queue_history

# --- Execute and Plot ---
if __name__ == "__main__":
    fixed_queues = evaluate_fixed_time()
    ai_queues = evaluate_ai_model()
    
    print("📊 Generating comparison plot...")
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 6))
    
    # Smooth the lines slightly so it looks clean (moving average of 10 seconds)
    def smooth(y, box_pts):
        box = np.ones(box_pts)/box_pts
        return np.convolve(y, box, mode='same')
        
    plt.plot(smooth(fixed_queues, 10), label='Traditional Fixed-Time (30s)', color='#e74c3c', linewidth=2, linestyle='--')
    plt.plot(smooth(ai_queues, 10), label='VisionX RL Model', color='#2ecc71', linewidth=3)
    
    plt.fill_between(range(SIM_STEPS), smooth(ai_queues, 10), color='#2ecc71', alpha=0.2)
    
    plt.title('Real Simulation Data: AI vs Traditional Control', fontsize=18, fontweight='bold', pad=15)
    plt.xlabel('Simulation Time (Seconds)', fontsize=12, fontweight='bold')
    plt.ylabel('Total Waiting Vehicles (Queue Length)', fontsize=12, fontweight='bold')
    plt.legend(fontsize=12)
    plt.xlim(0, SIM_STEPS)
    
    # Save the actual, non-fake plot
    plt.tight_layout()
    plt.savefig('real_ai_comparison.png', dpi=300)
    print("✅ Done! Plot saved as 'real_ai_comparison.png'")
