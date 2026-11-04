const express = require('express');
const cors = require('cors');
const WebSocket = require('ws');

const app = express();
app.use(cors());
app.use(express.json());

// ==========================================
// 1. Shared Intersection State (Single Source of Truth)
// ==========================================
let sharedState = {
    laneACount: 0,
    laneBCount: 0,
    laneCCount: 0,
    laneDCount: 0,
    activeSignal: "INITIALIZING...",
    isAiActive: false,
    systemMode: "AI_OPTIMIZED", // AI_OPTIMIZED, EMERGENCY_NS, EMERGENCY_EW, POLICE_STOP
    lastUpdate: Date.now()
};

// ==========================================
// 2. Python AI & React Dashboard Endpoints
// ==========================================

// Python AI pushes live traffic telemetry here
app.post('/api/traffic', (req, res) => {
    sharedState.laneACount = req.body.laneACount ?? sharedState.laneACount;
    sharedState.laneBCount = req.body.laneBCount ?? sharedState.laneBCount;
    sharedState.laneCCount = req.body.laneCCount ?? sharedState.laneCCount;
    sharedState.laneDCount = req.body.laneDCount ?? sharedState.laneDCount;
    sharedState.activeSignal = req.body.activeSignal ?? sharedState.activeSignal;
    sharedState.isAiActive = req.body.isAiActive ?? true;
    sharedState.lastUpdate = Date.now();
    res.status(200).json({ status: "OK" });
});

// React Dashboard / Python AI fetch current state and active commands
app.get('/api/traffic', (req, res) => {
    // Watchdog: If Python goes silent for >3 seconds, mark as offline
    if (Date.now() - sharedState.lastUpdate > 3000) {
        sharedState.isAiActive = false;
        if (sharedState.activeSignal !== "INITIALIZING...") {
            sharedState.activeSignal = "OFFLINE - Waiting for Agent...";
        }
    }
    res.json(sharedState);
});

// React Dashboard sends Manual Overrides (Emergency / Police)
app.post('/api/command', (req, res) => {
    const { command, displayName } = req.body;
    console.log(`🚨 Manual Override Received: ${command} (${displayName || 'Global'})`);
    sharedState.systemMode = command || "AI_OPTIMIZED";
    res.json({ status: "Override Active", mode: sharedState.systemMode });
});

// ==========================================
// 3. ROS 2 DDS WebSocket Bridge Connection
// ==========================================
let rosWs = null;
let isRosConnected = false;
const ROS_WS_URL = process.env.ROS_BRIDGE_URL || 'ws://localhost:9090';

function connectToRosBridge() {
    try {
        rosWs = new WebSocket(ROS_WS_URL);

        rosWs.on('open', () => {
            isRosConnected = true;
            console.log('✅ Connected to AURA ROS 2 DDS Network (ws://localhost:9090).');
            // Advertise emergency_path topic so ROS 2 network knows we intend to publish
            rosWs.send(JSON.stringify({
                op: 'advertise',
                topic: '/frontend/emergency_path',
                type: 'std_msgs/msg/String'
            }));
        });

        rosWs.on('message', (data) => {
            try {
                const parsed = JSON.parse(data.toString());
                if (parsed.topic === '/frontend/emergency_path') {
                    console.log(`[ROS2 Feedback] ${parsed.msg?.data}`);
                }
            } catch (err) {}
        });

        rosWs.on('error', (err) => {
            // Silently swallow connection refused when ROS 2 bridge is not active
            if (isRosConnected) {
                console.warn('⚠️ ROS Bridge connection error:', err.message);
            }
            isRosConnected = false;
        });

        rosWs.on('close', () => {
            if (isRosConnected) {
                console.log('🔌 ROS Bridge disconnected. Retrying in 5s...');
            }
            isRosConnected = false;
            setTimeout(connectToRosBridge, 5000);
        });
    } catch (e) {
        setTimeout(connectToRosBridge, 5000);
    }
}

connectToRosBridge();

// Phase 2 Tactical Dispatch: React Map dispatches ambulance route
app.post('/api/dispatch-ambulance', (req, res) => {
    const routeArray = req.body.route || [];
    const routeString = Array.isArray(routeArray) ? routeArray.join(',') : String(routeArray);

    console.log(`🚑 Dispatching Green Wave route: [${routeString}]`);
    sharedState.emergencyRoute = routeArray;
    sharedState.systemMode = 'GREEN_WAVE_DISPATCH';
    sharedState.lastUpdate = Date.now();

    const rosPayload = {
        op: 'publish',
        topic: '/frontend/emergency_path',
        msg: { data: routeString }
    };

    if (rosWs && rosWs.readyState === WebSocket.OPEN) {
        rosWs.send(JSON.stringify(rosPayload));
        console.log(`📡 Route successfully pushed to ROS 2 DDS network.`);
        return res.status(200).json({ message: "Green Wave Initiated via ROS 2", route: routeArray });
    } else {
        console.log(`ℹ️ ROS Bridge offline; route registered locally.`);
        return res.status(200).json({ message: "Green Wave Initiated (Standalone Mode)", route: routeArray });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: "healthy",
        uptime: process.uptime(),
        rosBridgeConnected: isRosConnected,
        aiActive: sharedState.isAiActive,
        systemMode: sharedState.systemMode
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 VisionX / AURA Backend Active on Port ${PORT}`);
    console.log(`   - REST Telemetry: http://localhost:${PORT}/api/traffic`);
    console.log(`   - Command Dispatch: http://localhost:${PORT}/api/command`);
    console.log(`   - Tactical Route: http://localhost:${PORT}/api/dispatch-ambulance`);
});
