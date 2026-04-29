const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// The Single Source of Truth
let sharedState = {
    laneACount: 0, laneBCount: 0, laneCCount: 0, laneDCount: 0,
    activeSignal: "INITIALIZING...",
    isAiActive: false,
    systemMode: "AI_OPTIMIZED", // AI_OPTIMIZED, EMERGENCY_NS, EMERGENCY_EW, POLICE_STOP
    lastUpdate: Date.now()
};

// 1. Python AI pushes live traffic data here
app.post('/api/traffic', (req, res) => {
    sharedState.laneACount = req.body.laneACount;
    sharedState.laneBCount = req.body.laneBCount;
    sharedState.laneCCount = req.body.laneCCount;
    sharedState.laneDCount = req.body.laneDCount;
    sharedState.activeSignal = req.body.activeSignal;
    sharedState.isAiActive = req.body.isAiActive;
    sharedState.lastUpdate = Date.now();
    res.sendStatus(200);
});

// 2. React / Python fetch the current state and commands
app.get('/api/traffic', (req, res) => {
    // Watchdog: If Python goes silent for 3 seconds, mark offline
    if (Date.now() - sharedState.lastUpdate > 3000) {
        sharedState.isAiActive = false;
        sharedState.activeSignal = "OFFLINE - Waiting for Agent...";
    }
    res.json(sharedState);
});

// 3. React Frontend sends Emergency Overrides here
app.post('/api/command', (req, res) => {
    const { command } = req.body; 
    console.log(`🚨 Manual Override Received: ${command}`);
    sharedState.systemMode = command; 
    res.json({ status: "Override Active", mode: command });
});

const PORT = 3000;
app.listen(PORT, () => console.log(`🚀 Pro Bridge Active on Port ${PORT}`));