import os
import sys
import random
import numpy as np
import collections
import torch
import torch.nn as nn
import torch.optim as optim
import traci

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

LANE_IDS = ["top0A0", "right0A0", "bottom0A0", "left0A0"]
TRAFFIC_LIGHT_ID = "A0"

class TrafficDQN(nn.Module):
    def __init__(self, input_size=4, output_size=4):
        super(TrafficDQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

Transition = collections.namedtuple('Transition', ('state', 'action', 'reward', 'next_state'))

class ReplayMemory:
    def __init__(self, capacity):
        self.memory = collections.deque(maxlen=capacity)
    def push(self, *args):
        self.memory.append(Transition(*args))
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
    def __len__(self):
        return len(self.memory)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = TrafficDQN(4, 4).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.0005)
memory = ReplayMemory(5000)
loss_fn = nn.MSELoss()

gamma, epsilon, epsilon_min, epsilon_decay, batch_size = 0.95, 1.0, 0.05, 0.992, 64

def get_state():
    return np.array([traci.edge.getLastStepHaltingNumber(l) for l in LANE_IDS], dtype=np.float32)

def train_model():
    if len(memory) < batch_size: return
    batch = Transition(*zip(*memory.sample(batch_size)))
    
    state_b = torch.FloatTensor(np.array(batch.state)).to(device)
    action_b = torch.LongTensor(batch.action).unsqueeze(1).to(device)
    reward_b = torch.FloatTensor(batch.reward).to(device)
    next_state_b = torch.FloatTensor(np.array(batch.next_state)).to(device)

    current_q = model(state_b).gather(1, action_b)
    next_q = model(next_state_b).max(1)[0].detach()
    loss = loss_fn(current_q.squeeze(), reward_b + (gamma * next_q))
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

def run_training():
    global epsilon
    traci.start(["sumo", "-c", "network_config.sumocfg", "--no-step-log", "true"])
    print(f"🚀 Training Brain on {device}...")

    state, step, total_reward = get_state(), 0, 0

    while step < 3000:
        action = random.randint(0, 3) if random.random() < epsilon else model(torch.FloatTensor(state).to(device)).argmax().item()
        target_phase = 0 if action in [0, 2] else 2
        current_phase = traci.trafficlight.getPhase(TRAFFIC_LIGHT_ID)

        if current_phase != target_phase:
            traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, 1 if current_phase == 0 else 3)
            for _ in range(3): traci.simulationStep()

        traci.trafficlight.setPhase(TRAFFIC_LIGHT_ID, target_phase)
        green_duration = max(10, min(int((state[0]+state[2] if target_phase == 0 else state[1]+state[3]) * 2), 45))
        for _ in range(green_duration): traci.simulationStep()

        next_state = get_state()
        reward = -sum(next_state) + ((sum(state) - sum(next_state)) * 2)
        
        memory.push(state, action, reward, next_state)
        train_model()

        state = next_state
        total_reward += reward
        step += 1
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        if step % 50 == 0:
            torch.save(model.state_dict(), "traffic_rl_model_final.pth")
            print(f"Step {step} | Reward: {total_reward:.1f} | Eps: {epsilon:.2f}")
            total_reward = 0
    traci.close()

if __name__ == "__main__": run_training()