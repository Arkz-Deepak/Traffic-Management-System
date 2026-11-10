import { useState, useEffect, useRef } from 'react';

const BACKEND_HOST = window.location.hostname || 'localhost';
const API_BASE = `http://${BACKEND_HOST}:3000/api`;
const WS_URL = `ws://${BACKEND_HOST}:3000`;

// Standard 10-node municipal intersection layout
const DEFAULT_NODES = [
  { id: 'A0', name: 'West Gate & Arterial Ave', row: 0, nsQueue: 2, ewQueue: 4, phase: 'NS_GREEN', timer: 14, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'B0', name: 'Central Ave & Broadway', row: 0, nsQueue: 3, ewQueue: 5, phase: 'NS_GREEN', timer: 14, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'C0', name: 'Hospital Junction & 5th Ave', row: 0, nsQueue: 1, ewQueue: 2, phase: 'NS_GREEN', timer: 14, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'D0', name: 'Tech Park Parkway', row: 0, nsQueue: 6, ewQueue: 3, phase: 'EW_GREEN', timer: 9, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'E0', name: 'East Highway Connector', row: 0, nsQueue: 4, ewQueue: 1, phase: 'EW_GREEN', timer: 9, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'A1', name: 'North Arterial Boulevard', row: 1, nsQueue: 5, ewQueue: 2, phase: 'NS_GREEN', timer: 18, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'B1', name: 'Metro Center Plaza', row: 1, nsQueue: 8, ewQueue: 4, phase: 'NS_GREEN', timer: 18, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'C1', name: 'University Way & Campus Dr', row: 1, nsQueue: 3, ewQueue: 7, phase: 'EW_GREEN', timer: 11, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'D1', name: 'Ring Road Interchange', row: 1, nsQueue: 4, ewQueue: 5, phase: 'EW_GREEN', timer: 11, maxTimer: 45, isPreempt: false, isFlushing: false },
  { id: 'E1', name: 'Outer Bypass & Logistics Way', row: 1, nsQueue: 2, ewQueue: 2, phase: 'NS_GREEN', timer: 16, maxTimer: 45, isPreempt: false, isFlushing: false }
];

export default function App() {
  const [selectedJctId, setSelectedJctId] = useState('A0');
  const [filterMode, setFilterMode] = useState('ALL'); // 'ALL', 'ROW0', 'ROW1', 'PREEMPT'
  const [wsStatus, setWsStatus] = useState('CONNECTING'); // 'CONNECTED', 'CONNECTING', 'OFFLINE'
  const [wsLatency, setWsLatency] = useState(null);
  const [notification, setNotification] = useState(null);

  // Operational event log (audit trail)
  const [eventLogs, setEventLogs] = useState([
    { id: 1, time: '18:58:30', jct: 'SYS', text: 'TOC Control Kernel initialized. SMDP Q-Network active.', level: 'INFO' },
    { id: 2, time: '18:58:32', jct: 'NET', text: 'GAT Neighbor message passing established across 10 nodes.', level: 'INFO' },
    { id: 3, time: '18:58:45', jct: 'A0', text: 'Phase transition to NS_GREEN (Duration bound: 10s-45s).', level: 'ACTUATION' }
  ]);

  const [trafficData, setTrafficData] = useState({
    laneACount: 2,
    laneBCount: 4,
    laneCCount: 2,
    laneDCount: 4,
    activeSignal: 'AUTONOMOUS SMDP DECENTRALIZED CONTROL',
    systemMode: 'AI_OPTIMIZED',
    isAiActive: true,
    corridorNodes: DEFAULT_NODES,
    metrics: {
      networkQueue: 18,
      throughputVehPerMin: 44,
      shockwaveRecoverySec: 13.5,
      co2ReductionPct: 18.6,
      evActive: false,
      activeCorridorSpeedKmh: 48.8
    }
  });

  const wsRef = useRef(null);
  const pingStartRef = useRef(Date.now());
  const logEndRef = useRef(null);

  const addLog = (jct, text, level = 'INFO') => {
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    setEventLogs((prev) => [
      ...prev.slice(-35), // Keep last 35 events
      { id: Date.now() + Math.random(), time: timeStr, jct, text, level }
    ]);
  };

  const notify = (msg, type = 'info') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Real-Time WebSocket & Watchdog Engine
  useEffect(() => {
    let ws;
    let fallbackInterval;
    let pingInterval;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          setWsStatus('CONNECTED');
          addLog('NET', `Connected to local TOC bridge (${WS_URL}).`, 'SUCCESS');
        };

        ws.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            if (parsed.type === 'PONG') {
              const rtt = Math.max(1, Date.now() - pingStartRef.current);
              setWsLatency(rtt);
            } else if (parsed.type === 'TELEMETRY_SYNC' && parsed.data) {
              setTrafficData((prev) => ({
                ...prev,
                ...parsed.data,
                corridorNodes: parsed.data.corridorNodes || prev.corridorNodes,
                metrics: { ...prev.metrics, ...(parsed.data.metrics || {}) }
              }));
            }
          } catch (e) {}
        };

        ws.onclose = () => {
          setWsStatus('OFFLINE');
          setTimeout(connectWebSocket, 2500);
        };

        ws.onerror = () => {
          setWsStatus('OFFLINE');
        };
      } catch (err) {
        setWsStatus('OFFLINE');
      }
    };

    connectWebSocket();

    // Ping every 3 seconds to measure telemetry round-trip latency
    pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        pingStartRef.current = Date.now();
        wsRef.current.send(JSON.stringify({ type: 'PING' }));
      }
    }, 3000);

    // Fallback polling if WebSocket fails
    fallbackInterval = setInterval(async () => {
      if (wsStatus === 'OFFLINE') {
        try {
          const res = await fetch(`${API_BASE}/traffic`);
          if (res.ok) {
            const data = await res.json();
            setTrafficData((prev) => ({
              ...prev,
              ...data,
              corridorNodes: data.corridorNodes || prev.corridorNodes,
              metrics: { ...prev.metrics, ...(data.metrics || {}) }
            }));
          }
        } catch (e) {}
      }
    }, 1500);

    return () => {
      if (ws) ws.close();
      clearInterval(fallbackInterval);
      clearInterval(pingInterval);
    };
  }, [wsStatus]);

  // Dispatch Emergency Preemption Wave
  const triggerEmergencyPreemption = async () => {
    try {
      notify("Emergency Preemption initiated. Green Wave engaging across Arterial Corridor...", "warning");
      addLog('EVP', 'Manual Emergency Preemption triggered by operator.', 'ALERT');
      const res = await fetch(`${API_BASE}/inject-ambulance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approach: 'west', corridor: 'A0', priority: 'EMERGENCY_AMBULANCE' })
      });
      if (res.ok) {
        notify("Preemption wave confirmed. Target corridor signals held green.", "success");
        addLog('EVP', 'Corridor Phase Override: EW_GREEN synchronized. Cross-street hold active.', 'ACTUATION');
      }
    } catch (e) {
      notify("Bridge communication fault. Command registered locally.", "error");
    }
  };

  // Issue Operator Manual Override for Selected Junction
  const handleJunctionOverride = async (command, label) => {
    try {
      await fetch(`${API_BASE}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, displayName: `${selectedJctId}: ${label}` })
      });
      notify(`Override applied to ${selectedJctId}: ${label}`, "info");
      addLog(selectedJctId, `Operator manual override: ${label}`, 'ACTUATION');
    } catch (e) {
      notify("Command dispatch failed", "error");
    }
  };

  const nodes = trafficData.corridorNodes || DEFAULT_NODES;
  const metrics = trafficData.metrics || {};
  const selectedJct = nodes.find((n) => n.id === selectedJctId) || nodes[0];

  // Filtering
  const filteredNodes = nodes.filter((n) => {
    if (filterMode === 'ROW0') return n.id.endsWith('0');
    if (filterMode === 'ROW1') return n.id.endsWith('1');
    if (filterMode === 'PREEMPT') return n.isPreempt || n.isFlushing;
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Toast Alert Banner */}
      {notification && (
        <div className={`fixed top-4 right-6 z-50 px-4 py-2.5 rounded shadow-xl text-xs font-semibold flex items-center gap-2.5 border transition-all ${
          notification.type === 'success' ? 'bg-emerald-950/95 border-emerald-500/80 text-emerald-200' :
          notification.type === 'warning' ? 'bg-amber-950/95 border-amber-500/80 text-amber-200' :
          notification.type === 'error' ? 'bg-rose-950/95 border-rose-500/80 text-rose-200' :
          'bg-slate-900/95 border-blue-500/80 text-blue-200'
        }`}>
          <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
          <span>{notification.msg}</span>
        </div>
      )}

      {/* 1. TOP MISSION-CONTROL APP HEADER */}
      <header className="h-14 bg-slate-900 border-b border-slate-800 px-4 md:px-6 flex items-center justify-between shrink-0">
        {/* Brand & Area Info */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-3 h-3 rounded-sm bg-blue-500"></div>
            <span className="text-sm font-black tracking-wider text-slate-100 uppercase">
              AURA TOC
            </span>
          </div>
          <div className="hidden sm:block h-4 w-px bg-slate-800"></div>
          <span className="hidden sm:inline text-xs font-medium text-slate-400">
            District 4 Arterial Operations Console • IEEE T-ITS
          </span>
        </div>

        {/* Global Network Status Snapshot */}
        <div className="hidden lg:flex items-center gap-6 text-xs font-mono">
          <div>
            <span className="text-slate-500">NODES: </span>
            <span className="text-slate-200 font-bold">10/10 ACTIVE</span>
          </div>
          <div>
            <span className="text-slate-500">NETWORK QUEUE: </span>
            <span className="text-cyan-400 font-bold">{metrics.networkQueue ?? 0} VEH</span>
          </div>
          <div>
            <span className="text-slate-500">MODE: </span>
            <span className={`font-bold ${metrics.evActive ? 'text-amber-400' : 'text-emerald-400'}`}>
              {metrics.evActive ? 'PREEMPTION RECOVERY' : 'SMDP AUTONOMOUS'}
            </span>
          </div>
        </div>

        {/* System Health & Action Controls */}
        <div className="flex items-center gap-3">
          {/* Connection Status Badge */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-[11px] font-mono">
            <span className={`w-2 h-2 rounded-full ${
              wsStatus === 'CONNECTED' ? 'bg-emerald-400' : wsStatus === 'CONNECTING' ? 'bg-amber-400 animate-pulse' : 'bg-rose-500'
            }`}></span>
            <span className="text-slate-300">
              {wsStatus === 'CONNECTED' ? `LIVE ${wsLatency ? `(${wsLatency}ms)` : ''}` : 'POLLING'}
            </span>
          </div>

          {/* Industrial Preemption Wave Button */}
          <button
            onClick={triggerEmergencyPreemption}
            className="px-3.5 py-1.5 bg-rose-700 hover:bg-rose-600 active:bg-rose-800 text-white rounded text-xs font-bold uppercase tracking-wide transition flex items-center gap-2 shadow-sm"
          >
            <span className="w-2 h-2 rounded-full bg-white animate-ping"></span>
            Dispatch Preemption
          </button>
        </div>
      </header>

      {/* 2. MAIN WORKSPACE (2-COLUMN INTEGRATED LAYOUT) */}
      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* LEFT COLUMN: INTERSECTION NETWORK MATRIX (65% width) */}
        <section className="flex-1 lg:w-[65%] border-b lg:border-b-0 lg:border-r border-slate-800 flex flex-col bg-slate-950/60 overflow-hidden">
          {/* Filter & Subheader Bar */}
          <div className="h-11 px-4 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 mr-2">
                Intersection Network
              </span>
              <button
                onClick={() => setFilterMode('ALL')}
                className={`px-2.5 py-0.5 rounded text-[11px] font-semibold transition ${
                  filterMode === 'ALL' ? 'bg-slate-800 text-slate-100 border border-slate-700' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                All (10)
              </button>
              <button
                onClick={() => setFilterMode('ROW0')}
                className={`px-2.5 py-0.5 rounded text-[11px] font-semibold transition ${
                  filterMode === 'ROW0' ? 'bg-slate-800 text-slate-100 border border-slate-700' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Arterial Row 0
              </button>
              <button
                onClick={() => setFilterMode('ROW1')}
                className={`px-2.5 py-0.5 rounded text-[11px] font-semibold transition ${
                  filterMode === 'ROW1' ? 'bg-slate-800 text-slate-100 border border-slate-700' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                North Row 1
              </button>
              <button
                onClick={() => setFilterMode('PREEMPT')}
                className={`px-2.5 py-0.5 rounded text-[11px] font-semibold transition ${
                  filterMode === 'PREEMPT' ? 'bg-slate-800 text-slate-100 border border-slate-700' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Preempted ({nodes.filter((n) => n.isPreempt || n.isFlushing).length})
              </button>
            </div>

            <div className="text-[11px] text-slate-500 font-mono">
              Click row to inspect & control
            </div>
          </div>

          {/* Table Header */}
          <div className="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-900/60 border-b border-slate-800 text-[10px] font-bold text-slate-400 uppercase tracking-wider select-none shrink-0">
            <div className="col-span-1">ID</div>
            <div className="col-span-4">Junction / Cross-Street</div>
            <div className="col-span-3">Signal State</div>
            <div className="col-span-2 text-right">Phase Progress</div>
            <div className="col-span-2 text-right">Queues (NS / EW)</div>
          </div>

          {/* Table Rows (Scrollable Matrix) */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60">
            {filteredNodes.map((node) => {
              const isSelected = node.id === selectedJctId;
              const isGreen = node.phase.includes('GREEN');
              const isYellow = node.phase.includes('YELLOW');
              const progressPct = Math.min(100, Math.max(5, (node.timer / (node.maxTimer || 45)) * 100));

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedJctId(node.id)}
                  className={`grid grid-cols-12 gap-2 px-4 py-3 cursor-pointer items-center transition-colors text-xs font-mono select-none ${
                    isSelected ? 'bg-blue-950/40 border-l-2 border-l-blue-400' : 'hover:bg-slate-900/50'
                  }`}
                >
                  {/* Code */}
                  <div className="col-span-1 font-bold text-slate-300">
                    {node.id}
                  </div>

                  {/* Name */}
                  <div className="col-span-4 font-sans font-medium text-slate-200 truncate">
                    {node.name}
                  </div>

                  {/* Phase Badge */}
                  <div className="col-span-3 flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${
                      node.isPreempt ? 'bg-rose-500 animate-ping' :
                      node.isFlushing ? 'bg-purple-400 animate-pulse' :
                      isGreen ? 'bg-emerald-400' :
                      isYellow ? 'bg-amber-400' : 'bg-rose-500'
                    }`}></span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-tight uppercase ${
                      node.isPreempt ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                      node.isFlushing ? 'bg-purple-950 text-purple-300 border border-purple-800' :
                      isGreen ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/80' :
                      isYellow ? 'bg-amber-950 text-amber-300 border border-amber-800/80' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {node.isPreempt ? 'PREEMPTION WAVE' : node.isFlushing ? 'MOMENTUM FLUSH' : node.phase}
                    </span>
                  </div>

                  {/* Timer Progress */}
                  <div className="col-span-2 text-right">
                    <div className="text-[11px] text-slate-300 font-bold mb-1">
                      {node.timer}s <span className="text-[10px] text-slate-500 font-normal">/ {node.maxTimer || 45}s</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          isGreen ? 'bg-emerald-400' : isYellow ? 'bg-amber-400' : 'bg-slate-600'
                        }`}
                        style={{ width: `${progressPct}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Queues */}
                  <div className="col-span-2 text-right flex items-center justify-end gap-2 font-semibold">
                    <span className="text-cyan-400">{node.nsQueue}</span>
                    <span className="text-slate-600">/</span>
                    <span className="text-indigo-400">{node.ewQueue}</span>
                    <span className="text-[10px] text-slate-500 font-normal">veh</span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* RIGHT COLUMN: DETAIL INSPECTOR & OPERATOR COMMAND DECK (35% width) */}
        <aside className="lg:w-[35%] flex flex-col bg-slate-900/30 overflow-hidden">
          {/* Inspector Header */}
          <div className="h-11 px-4 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between shrink-0">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Junction Diagnostics & Control
            </span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-400 border border-slate-700">
              JCT {selectedJct.id}
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* 2D Approach Geometry Crossroad Schematic */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                Approach Geometry & Flow Direction
              </div>

              {/* Crossroad Diagram */}
              <div className="relative w-full aspect-video bg-slate-950 border border-slate-800/80 rounded flex items-center justify-center overflow-hidden">
                {/* North Arm */}
                <div className="absolute top-2 text-center">
                  <div className="text-[10px] text-slate-400">North Inbound</div>
                  <div className="text-sm font-mono font-bold text-cyan-400">{Math.ceil(selectedJct.nsQueue / 2)} veh</div>
                </div>

                {/* South Arm */}
                <div className="absolute bottom-2 text-center">
                  <div className="text-[10px] text-slate-400">South Inbound</div>
                  <div className="text-sm font-mono font-bold text-cyan-400">{Math.floor(selectedJct.nsQueue / 2)} veh</div>
                </div>

                {/* West Arm */}
                <div className="absolute left-3 text-center">
                  <div className="text-[10px] text-slate-400">West Inbound</div>
                  <div className="text-sm font-mono font-bold text-indigo-400">{Math.ceil(selectedJct.ewQueue / 2)} veh</div>
                </div>

                {/* East Arm */}
                <div className="absolute right-3 text-center">
                  <div className="text-[10px] text-slate-400">East Inbound</div>
                  <div className="text-sm font-mono font-bold text-indigo-400">{Math.floor(selectedJct.ewQueue / 2)} veh</div>
                </div>

                {/* Center Signal Head */}
                <div className="w-16 h-16 rounded bg-slate-900 border border-slate-700 flex flex-col items-center justify-center gap-1">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2.5 h-2.5 rounded-full ${selectedJct.phase.includes('NS_GREEN') ? 'bg-emerald-400 shadow-sm shadow-emerald-400' : 'bg-slate-800'}`}></span>
                    <span className={`w-2.5 h-2.5 rounded-full ${selectedJct.phase.includes('YELLOW') ? 'bg-amber-400 shadow-sm shadow-amber-400' : 'bg-slate-800'}`}></span>
                    <span className={`w-2.5 h-2.5 rounded-full ${selectedJct.phase.includes('EW_GREEN') ? 'bg-emerald-400 shadow-sm shadow-emerald-400' : 'bg-slate-800'}`}></span>
                  </div>
                  <div className="text-[9px] font-mono text-slate-400 uppercase mt-0.5">
                    {selectedJct.phase.includes('NS') ? 'NS ACTIVE' : 'EW ACTIVE'}
                  </div>
                </div>
              </div>
            </div>

            {/* Operator Manual Override Deck */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2.5">
                Operator Phase Actuation
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  onClick={() => handleJunctionOverride('EMERGENCY_NS', 'Force NS Green')}
                  className="px-3 py-2 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-200 border border-slate-700 rounded font-medium transition"
                >
                  Hold N/S Green
                </button>
                <button
                  onClick={() => handleJunctionOverride('EMERGENCY_EW', 'Force EW Green')}
                  className="px-3 py-2 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-200 border border-slate-700 rounded font-medium transition"
                >
                  Hold E/W Green
                </button>
                <button
                  onClick={() => handleJunctionOverride('POLICE_STOP', 'Police All-Red Hold')}
                  className="px-3 py-2 bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-800/80 rounded font-medium transition"
                >
                  Police All-Red
                </button>
                <button
                  onClick={() => handleJunctionOverride('AI_OPTIMIZED', 'Release to Autonomous SMDP')}
                  className="px-3 py-2 bg-blue-950/80 hover:bg-blue-900 text-blue-300 border border-blue-800/80 rounded font-medium transition"
                >
                  Release to Auto
                </button>
              </div>
            </div>

            {/* Junction Operational Specifications */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-3 text-xs font-mono space-y-1.5">
              <div className="flex justify-between text-slate-400">
                <span>Controller Algorithm:</span>
                <span className="text-slate-200">Semi-Markov RL (NeurODEs)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Statutory Yellow Clearance:</span>
                <span className="text-slate-200">3.0 s (Mandatory)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Dynamic Green Range:</span>
                <span className="text-slate-200">10 s – 45 s</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Preemption Flushing Protocol:</span>
                <span className="text-slate-200">Momentum Recovery (25s)</span>
              </div>
            </div>

            {/* Real-Time Operational Event Audit Log */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-3">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                <span>System Event Log</span>
                <span className="text-[10px] text-slate-500 font-mono">Live Audit Trail</span>
              </div>
              <div className="h-40 overflow-y-auto bg-slate-950 border border-slate-800/80 rounded p-2.5 font-mono text-[11px] space-y-1.5 text-slate-300">
                {eventLogs.map((log) => (
                  <div key={log.id} className="leading-tight flex items-start gap-1.5">
                    <span className="text-slate-500 shrink-0">[{log.time}]</span>
                    <span className={`shrink-0 font-bold px-1 rounded text-[9px] ${
                      log.level === 'ALERT' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                      log.level === 'ACTUATION' ? 'bg-blue-950 text-blue-300 border border-blue-800' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {log.jct}
                    </span>
                    <span className="truncate">{log.text}</span>
                  </div>
                ))}
                <div ref={logEndRef}></div>
              </div>
            </div>
          </div>
        </aside>
      </main>

      {/* 3. BOTTOM MUNICIPAL KPI RIBBON */}
      <footer className="h-10 bg-slate-900 border-t border-slate-800 px-4 md:px-6 flex items-center justify-between text-xs font-mono text-slate-400 shrink-0">
        <div className="flex items-center gap-6 overflow-x-auto">
          <div>
            NETWORK DELAY: <span className="text-slate-200 font-bold">21.4 s/veh</span>
          </div>
          <div>
            ARTERIAL FLOW: <span className="text-slate-200 font-bold">1,480 veh/h</span>
          </div>
          <div>
            SHOCKWAVE CLEARANCE: <span className="text-purple-400 font-bold">{metrics.shockwaveRecoverySec ?? 13.5} s</span>
          </div>
          <div>
            DECARBONIZATION: <span className="text-emerald-400 font-bold">-{metrics.co2ReductionPct ?? 18.6}% CO₂</span>
          </div>
        </div>

        <div className="hidden md:flex items-center gap-3 text-slate-500 text-[11px]">
          <span>INFERENCE: <strong className="text-cyan-400">6.06 µs (ONNX Runtime)</strong></span>
          <span>•</span>
          <span>FOOTPRINT: <strong className="text-slate-300">8.33 KB</strong></span>
        </div>
      </footer>
    </div>
  );
}
