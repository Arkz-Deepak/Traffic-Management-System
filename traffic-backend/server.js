const http = require('http');
const express = require('express');
const cors = require('cors');
const WebSocket = require('ws');

const app = express();
app.use(cors());
app.use(express.json());

// ==========================================
// 1. Shared Multi-Intersection State (Single Source of Truth)
// ==========================================
const DEFAULT_NODES = [
    { id: 'A0', name: 'West Gate (A0)', nsQueue: 0, ewQueue: 0, phase: 'NS_GREEN', timer: 12, isPreempt: false, isFlushing: false },
    { id: 'B0', name: 'Central Ave (B0)', nsQueue: 0, ewQueue: 0, phase: 'NS_GREEN', timer: 12, isPreempt: false, isFlushing: false },
    { id: 'C0', name: 'Hospital Jct (C0)', nsQueue: 0, ewQueue: 0, phase: 'NS_GREEN', timer: 12, isPreempt: false, isFlushing: false },
    { id: 'D0', name: 'Tech Park (D0)', nsQueue: 0, ewQueue: 0, phase: 'EW_GREEN', timer: 8, isPreempt: false, isFlushing: false },
    { id: 'E0', name: 'East Highway (E0)', nsQueue: 0, ewQueue: 0, phase: 'EW_GREEN', timer: 8, isPreempt: false, isFlushing: false },
    { id: 'A1', name: 'North Arterial (A1)', nsQueue: 0, ewQueue: 0, phase: 'NS_GREEN', timer: 15, isPreempt: false, isFlushing: false },
    { id: 'B1', name: 'Metro Center (B1)', nsQueue: 0, ewQueue: 0, phase: 'NS_GREEN', timer: 15, isPreempt: false, isFlushing: false },
    { id: 'C1', name: 'University Way (C1)', nsQueue: 0, ewQueue: 0, phase: 'EW_GREEN', timer: 10, isPreempt: false, isFlushing: false },
    { id: 'D1', name: 'Ring Road (D1)', nsQueue: 0, ewQueue: 0, phase: 'EW_GREEN', timer: 10, isPreempt: false, isFlushing: false },
    { id: 'E1', name: 'Outer Bypass (E1)', nsQueue: 0, ewQueue: 0, phase: 'NS_GREEN', timer: 14, isPreempt: false, isFlushing: false }
];

let sharedState = {
    // Phase 1 Single Intersection
    laneACount: 0,
    laneBCount: 0,
    laneCCount: 0,
    laneDCount: 0,
    activeSignal: "INITIALIZING...",
    isAiActive: false,
    systemMode: "AI_OPTIMIZED", // AI_OPTIMIZED, EMERGENCY_NS, EMERGENCY_EW, POLICE_STOP
    
    // Phase 2 Multi-Node Corridor & Grid
    corridorNodes: JSON.parse(JSON.stringify(DEFAULT_NODES)),
    
    // Real-Time System Metrics
    metrics: {
        networkQueue: 0,
        throughputVehPerMin: 42,
        shockwaveRecoverySec: 14.8,
        co2ReductionPct: 18.4,
        evActive: false,
        activeCorridorSpeedKmh: 48.5
    },

    // Emergency Vehicle Queue for TraCI
    pendingAmbulanceDispatch: null,
    emergencyRoute: [],
    
    lastUpdate: Date.now()
};

// ==========================================
// 2. HTTP Server & WebSocket Broadcasting Hub
// ==========================================
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const clientSockets = new Set();

wss.on('connection', (ws) => {
    clientSockets.add(ws);
    // Send immediate snapshot on connect
    ws.send(JSON.stringify({ type: 'TELEMETRY_SYNC', data: sharedState }));

    ws.on('close', () => {
        clientSockets.delete(ws);
    });

    ws.on('message', (msg) => {
        try {
            const parsed = JSON.parse(msg);
            if (parsed.type === 'PING') {
                ws.send(JSON.stringify({ type: 'PONG', timestamp: Date.now() }));
            }
        } catch (e) {}
    });
});

function broadcastTelemetry() {
    if (clientSockets.size === 0) return;
    const payload = JSON.stringify({ type: 'TELEMETRY_SYNC', data: sharedState });
    for (const ws of clientSockets) {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(payload);
        }
    }
}

// ==========================================
// 3. REST Endpoints for Python AI & React Dashboard
// ==========================================

// Python AI pushes live traffic telemetry here
app.post('/api/traffic', (req, res) => {
    // Update Single Intersection
    sharedState.laneACount = req.body.laneACount ?? sharedState.laneACount;
    sharedState.laneBCount = req.body.laneBCount ?? sharedState.laneBCount;
    sharedState.laneCCount = req.body.laneCCount ?? sharedState.laneCCount;
    sharedState.laneDCount = req.body.laneDCount ?? sharedState.laneDCount;
    sharedState.activeSignal = req.body.activeSignal ?? sharedState.activeSignal;
    sharedState.isAiActive = req.body.isAiActive ?? true;
    
    // Update Multi-Intersection Corridor if provided
    if (Array.isArray(req.body.corridorNodes)) {
        sharedState.corridorNodes = req.body.corridorNodes;
    }
    
    // Update Metrics if provided
    if (req.body.metrics) {
        sharedState.metrics = { ...sharedState.metrics, ...req.body.metrics };
    }
    
    sharedState.lastUpdate = Date.now();
    
    // Broadcast live over WebSocket
    broadcastTelemetry();
    
    res.status(200).json({ status: "OK" });
});

// React Dashboard / Python AI fetch current state and active commands
app.get('/api/traffic', (req, res) => {
    // Watchdog: If Python goes silent for >3 seconds, mark as offline
    if (Date.now() - sharedState.lastUpdate > 3000) {
        sharedState.isAiActive = false;
        if (sharedState.activeSignal !== "INITIALIZING...") {
            sharedState.activeSignal = "OFFLINE - Waiting for Simulation...";
        }
    }
    res.json(sharedState);
});

// React Dashboard sends Manual Overrides (Emergency / Police)
app.post('/api/command', (req, res) => {
    const { command, displayName } = req.body;
    console.log(`🚨 Manual Override Received: ${command} (${displayName || 'Global'})`);
    sharedState.systemMode = command || "AI_OPTIMIZED";
    sharedState.lastUpdate = Date.now();
    broadcastTelemetry();
    res.json({ status: "Override Active", mode: sharedState.systemMode });
});

// Emergency Ambulance Injection Endpoint (One-Click Dashboard Trigger)
app.post('/api/inject-ambulance', (req, res) => {
    const { approach, priority, corridor } = req.body;
    console.log(`🚑 One-Click Emergency Vehicle Injection Triggered! Approach: ${approach || 'north'}, Corridor: ${corridor || 'A0'}`);
    
    sharedState.pendingAmbulanceDispatch = {
        id: `amb_${Date.now()}`,
        approach: approach || 'north',
        corridor: corridor || 'A0',
        timestamp: Date.now()
    };
    sharedState.metrics.evActive = true;
    sharedState.systemMode = 'EMERGENCY_PREEMPTION';
    sharedState.lastUpdate = Date.now();
    
    broadcastTelemetry();
    res.status(200).json({
        success: true,
        message: "Emergency Ambulance Injected into TraCI Simulation Queue",
        dispatch: sharedState.pendingAmbulanceDispatch
    });
});

// Python TraCI Agent polls for pending ambulance injection
app.get('/api/pending-ambulance', (req, res) => {
    const pending = sharedState.pendingAmbulanceDispatch;
    sharedState.pendingAmbulanceDispatch = null; // Consume dispatch
    res.json({ pendingDispatch: pending });
});

// Phase 2 Tactical Dispatch: React Map dispatches ambulance route
app.post('/api/dispatch-ambulance', (req, res) => {
    const routeArray = req.body.route || [];
    const routeString = Array.isArray(routeArray) ? routeArray.join(',') : String(routeArray);

    console.log(`🚑 Dispatching Green Wave route: [${routeString}]`);
    sharedState.emergencyRoute = routeArray;
    sharedState.systemMode = 'GREEN_WAVE_DISPATCH';
    sharedState.metrics.evActive = true;
    sharedState.lastUpdate = Date.now();

    // Trigger local simulation injection
    sharedState.pendingAmbulanceDispatch = {
        id: `amb_route_${Date.now()}`,
        route: routeArray,
        timestamp: Date.now()
    };

    const rosPayload = {
        op: 'publish',
        topic: '/frontend/emergency_path',
        msg: { data: routeString }
    };

    if (rosWs && rosWs.readyState === WebSocket.OPEN) {
        rosWs.send(JSON.stringify(rosPayload));
        console.log(`📡 Route successfully pushed to ROS 2 DDS network.`);
        broadcastTelemetry();
        return res.status(200).json({ message: "Green Wave Initiated via ROS 2", route: routeArray });
    } else {
        console.log(`ℹ️ ROS Bridge offline; route registered locally.`);
        broadcastTelemetry();
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
        systemMode: sharedState.systemMode,
        connectedClients: clientSockets.size
    });
});

// ==========================================
// 4. ROS 2 DDS WebSocket Bridge Connection
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

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`🚀 AURA Real-Time Telemetry & WebSocket Bridge Active on Port ${PORT}`);
    console.log(`   - REST Telemetry:   http://localhost:${PORT}/api/traffic`);
    console.log(`   - WebSocket Stream: ws://localhost:${PORT}`);
    console.log(`   - Emergency Inject: http://localhost:${PORT}/api/inject-ambulance`);
    console.log(`   - Tactical Route:   http://localhost:${PORT}/api/dispatch-ambulance`);
});
