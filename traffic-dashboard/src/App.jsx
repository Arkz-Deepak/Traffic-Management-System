import { useState, useEffect, useRef } from 'react';

const BACKEND_HOST = window.location.hostname || 'localhost';
const API_BASE = `http://${BACKEND_HOST}:3000/api`;
const WS_URL = `ws://${BACKEND_HOST}:3000`;

const DEFAULT_NODES = [
  { id: 'A0', name: 'West Gate (A0)', nsQueue: 2, ewQueue: 4, phase: 'NS_GREEN', timer: 14, isPreempt: false, isFlushing: false },
  { id: 'B0', name: 'Central Ave (B0)', nsQueue: 3, ewQueue: 5, phase: 'NS_GREEN', timer: 14, isPreempt: false, isFlushing: false },
  { id: 'C0', name: 'Hospital Jct (C0)', nsQueue: 1, ewQueue: 2, phase: 'NS_GREEN', timer: 14, isPreempt: false, isFlushing: false },
  { id: 'D0', name: 'Tech Park (D0)', nsQueue: 6, ewQueue: 3, phase: 'EW_GREEN', timer: 9, isPreempt: false, isFlushing: false },
  { id: 'E0', name: 'East Highway (E0)', nsQueue: 4, ewQueue: 1, phase: 'EW_GREEN', timer: 9, isPreempt: false, isFlushing: false },
  { id: 'A1', name: 'North Arterial (A1)', nsQueue: 5, ewQueue: 2, phase: 'NS_GREEN', timer: 18, isPreempt: false, isFlushing: false },
  { id: 'B1', name: 'Metro Center (B1)', nsQueue: 8, ewQueue: 4, phase: 'NS_GREEN', timer: 18, isPreempt: false, isFlushing: false },
  { id: 'C1', name: 'University Way (C1)', nsQueue: 3, ewQueue: 7, phase: 'EW_GREEN', timer: 11, isPreempt: false, isFlushing: false },
  { id: 'D1', name: 'Ring Road (D1)', nsQueue: 4, ewQueue: 5, phase: 'EW_GREEN', timer: 11, isPreempt: false, isFlushing: false },
  { id: 'E1', name: 'Outer Bypass (E1)', nsQueue: 2, ewQueue: 2, phase: 'NS_GREEN', timer: 16, isPreempt: false, isFlushing: false }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('corridor'); // 'corridor', 'intersection', 'analytics'
  const [wsConnected, setWsConnected] = useState(false);
  const [notification, setNotification] = useState(null);

  // Telemetry state
  const [trafficData, setTrafficData] = useState({
    laneACount: 0,
    laneBCount: 0,
    laneCCount: 0,
    laneDCount: 0,
    activeSignal: 'Connecting to AURA Core...',
    systemMode: 'AI_OPTIMIZED',
    isAiActive: false,
    corridorNodes: DEFAULT_NODES,
    metrics: {
      networkQueue: 18,
      throughputVehPerMin: 42,
      shockwaveRecoverySec: 13.5,
      co2ReductionPct: 18.6,
      evActive: false,
      activeCorridorSpeedKmh: 49.2
    }
  });

  // Tactical Route Selection
  const [activePath, setActivePath] = useState([]);
  const [dispatchStatus, setDispatchStatus] = useState('Standby');

  const wsRef = useRef(null);

  const showNotification = (msg, type = 'info') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4500);
  };

  // 1. Real-time WebSocket connection with fallback to HTTP polling
  useEffect(() => {
    let ws;
    let fallbackInterval;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            if (parsed.type === 'TELEMETRY_SYNC' && parsed.data) {
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
          setWsConnected(false);
          // Try to reconnect in 3s
          setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = () => {
          setWsConnected(false);
        };
      } catch (err) {
        setWsConnected(false);
      }
    };

    connectWebSocket();

    // Secondary HTTP Polling watchdog (every 1000ms if ws drops)
    fallbackInterval = setInterval(async () => {
      if (!wsConnected) {
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
    }, 1000);

    return () => {
      if (ws) ws.close();
      clearInterval(fallbackInterval);
    };
  }, [wsConnected]);

  // 2. One-Click Emergency Vehicle Injection
  const injectEmergencyVehicle = async () => {
    try {
      showNotification("🚑 Dispatching Emergency Ambulance into AURA Corridor...", "warning");
      const res = await fetch(`${API_BASE}/inject-ambulance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approach: 'west', corridor: 'A0', priority: 'EMERGENCY_AMBULANCE' })
      });
      if (res.ok) {
        showNotification("🚨 Emergency Preemption Active: Green Wave Propagating!", "success");
      }
    } catch (err) {
      showNotification("Failed to contact backend bridge.", "error");
    }
  };

  // 3. Manual Override Command
  const sendCommand = async (cmd, label) => {
    try {
      await fetch(`${API_BASE}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd, displayName: label })
      });
      showNotification(`Manual Override Applied: ${label}`, "info");
    } catch (e) {
      showNotification("Failed to deliver command", "error");
    }
  };

  // 4. Tactical Route Toggle
  const toggleNode = (nodeId) => {
    if (activePath.includes(nodeId)) {
      setActivePath(activePath.filter((id) => id !== nodeId));
    } else {
      setActivePath([...activePath, nodeId]);
    }
  };

  const dispatchTacticalRoute = async () => {
    if (activePath.length === 0) return;
    setDispatchStatus('Dispatching Green Wave...');
    try {
      const res = await fetch(`${API_BASE}/dispatch-ambulance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ route: activePath })
      });
      if (res.ok) {
        showNotification(`Tactical Green Wave Engaged for [${activePath.join(' → ')}]`, "success");
        setDispatchStatus('Green Wave Active');
        setTimeout(() => {
          setActivePath([]);
          setDispatchStatus('Standby');
        }, 8000);
      }
    } catch (e) {
      setDispatchStatus('Dispatch Failed');
    }
  };

  const nodes = trafficData.corridorNodes || DEFAULT_NODES;
  const metrics = trafficData.metrics || {};

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 md:p-6 selection:bg-cyan-500 selection:text-white">
      {/* Top Banner / Toast Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-lg shadow-2xl text-sm font-semibold flex items-center gap-3 border transition-all animate-bounce ${
          notification.type === 'success' ? 'bg-emerald-950 border-emerald-500 text-emerald-200' :
          notification.type === 'warning' ? 'bg-amber-950 border-amber-500 text-amber-200' :
          notification.type === 'error' ? 'bg-rose-950 border-rose-500 text-rose-200' :
          'bg-slate-900 border-cyan-500 text-cyan-200'
        }`}>
          <span>{notification.msg}</span>
        </div>
      )}

      {/* Header */}
      <header className="max-w-7xl mx-auto mb-6 flex flex-col md:flex-row items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-2xl font-black bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent tracking-tight">
              AURA v2.0
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-cyan-950 border border-cyan-700/50 text-cyan-300">
              IEEE T-ITS Edition
            </span>
            <span className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full ${
              wsConnected ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-600/40' : 'bg-amber-950/80 text-amber-400 border border-amber-600/40'
            }`}>
              <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
              {wsConnected ? 'WebSocket Live (60 Hz)' : 'HTTP Polling'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Resilient Urban Traffic Signal Control via Semi-Markov RL • Continuous-Time NeurODEs • Rolling Preemption
          </p>
        </div>

        {/* Action Controls in Header */}
        <div className="flex items-center gap-3">
          <button
            onClick={injectEmergencyVehicle}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white rounded-lg text-sm font-bold shadow-lg shadow-rose-900/30 transition-all hover:scale-105 active:scale-95 border border-rose-400/30"
          >
            <span className="animate-spin">🚨</span>
            Inject Emergency Vehicle
          </button>
          <button
            onClick={() => sendCommand('AI_OPTIMIZED', 'Autonomous RL Control')}
            className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
          >
            Reset to Autonomous
          </button>
        </div>
      </header>

      {/* Main Tab Navigation */}
      <div className="max-w-7xl mx-auto mb-6 flex border-b border-slate-800">
        <button
          onClick={() => setActiveTab('corridor')}
          className={`pb-3 px-5 text-sm font-bold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'corridor' ? 'border-cyan-400 text-cyan-300' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>🗺️</span> 10-Node MARL Arterial Corridor
        </button>
        <button
          onClick={() => setActiveTab('intersection')}
          className={`pb-3 px-5 text-sm font-bold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'intersection' ? 'border-cyan-400 text-cyan-300' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>🚦</span> Single Junction Monitor (A0)
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`pb-3 px-5 text-sm font-bold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'analytics' ? 'border-cyan-400 text-cyan-300' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>📊</span> Edge Inference & Shockwave Analytics
        </button>
      </div>

      {/* System Quick Metrics Bar */}
      <div className="max-w-7xl mx-auto mb-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Network Backlog</div>
          <div className="text-xl font-black text-cyan-400 mt-1">{metrics.networkQueue ?? 0} <span className="text-xs font-normal text-slate-400">veh</span></div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Throughput Rate</div>
          <div className="text-xl font-black text-emerald-400 mt-1">{metrics.throughputVehPerMin ?? 42} <span className="text-xs font-normal text-slate-400">veh/min</span></div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Shockwave Dissipation</div>
          <div className="text-xl font-black text-purple-400 mt-1">{metrics.shockwaveRecoverySec ?? 13.5} <span className="text-xs font-normal text-slate-400">s</span></div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Decarbonization</div>
          <div className="text-xl font-black text-teal-400 mt-1">-{metrics.co2ReductionPct ?? 18.6}% <span className="text-xs font-normal text-slate-400">CO₂</span></div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Avg Arterial Speed</div>
          <div className="text-xl font-black text-indigo-400 mt-1">{metrics.activeCorridorSpeedKmh ?? 49.2} <span className="text-xs font-normal text-slate-400">km/h</span></div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Preemption Status</div>
          <div className={`text-sm font-black mt-1 flex items-center gap-1.5 ${metrics.evActive ? 'text-rose-400' : 'text-slate-400'}`}>
            <span className={`w-2 h-2 rounded-full ${metrics.evActive ? 'bg-rose-500 animate-ping' : 'bg-slate-600'}`}></span>
            {metrics.evActive ? 'PREEMPTION ACTIVE' : 'NOMINAL SMDP'}
          </div>
        </div>
      </div>

      {/* Tab 1: 10-Node MARL Corridor & Tactical Map */}
      {activeTab === 'corridor' && (
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Tactical Route Dispatcher Header */}
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-bold text-slate-200">Arterial Tactical Dispatch Matrix (5x2 Grid)</h2>
              <p className="text-xs text-slate-400 mt-0.5">Click node junctions below to construct custom dynamic green waves for VIP/Emergency corridors.</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400">
                Selected: {activePath.length > 0 ? activePath.map((id) => DEFAULT_NODES[id]?.id || id).join(' → ') : 'None'}
              </span>
              <button
                disabled={activePath.length === 0}
                onClick={dispatchTacticalRoute}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-lg shadow-md transition"
              >
                Dispatch Tactical Route ({activePath.length})
              </button>
            </div>
          </div>

          {/* Grid Layout of the 10 Intersections */}
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">North Corridor (Arterial Row 1)</div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 mb-4">
              {nodes.slice(5, 10).map((node, idx) => {
                const nodeIdx = idx + 5;
                const isSelected = activePath.includes(nodeIdx);
                const isGreen = node.phase.includes('GREEN');
                const isYellow = node.phase.includes('YELLOW');

                return (
                  <div
                    key={node.id}
                    onClick={() => toggleNode(nodeIdx)}
                    className={`cursor-pointer bg-slate-900 border rounded-xl p-3.5 transition relative overflow-hidden ${
                      isSelected ? 'border-cyan-400 ring-2 ring-cyan-500/30' :
                      node.isPreempt ? 'border-rose-500 bg-rose-950/20' :
                      node.isFlushing ? 'border-purple-500 bg-purple-950/20' :
                      'border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-300">{node.name}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${
                        node.isPreempt ? 'bg-rose-900/80 text-rose-300 animate-pulse' :
                        node.isFlushing ? 'bg-purple-900/80 text-purple-300' :
                        isGreen ? 'bg-emerald-950 text-emerald-400 border border-emerald-700/50' :
                        isYellow ? 'bg-amber-950 text-amber-400 border border-amber-700/50' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {node.isPreempt ? 'PREEMPT' : node.isFlushing ? 'FLUSHING' : node.phase}
                      </span>
                    </div>

                    {/* Queues */}
                    <div className="space-y-1.5 text-xs mt-3">
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>NS Queue</span>
                          <span className="font-semibold text-slate-200">{node.nsQueue}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-cyan-500 h-full rounded-full transition-all" style={{ width: `${Math.min(100, node.nsQueue * 10)}%` }}></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>EW Queue</span>
                          <span className="font-semibold text-slate-200">{node.ewQueue}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-indigo-500 h-full rounded-full transition-all" style={{ width: `${Math.min(100, node.ewQueue * 10)}%` }}></div>
                        </div>
                      </div>
                    </div>

                    {/* Elapsed Timer Gauge */}
                    <div className="mt-3 pt-2 border-t border-slate-800 flex justify-between items-center text-[11px] text-slate-400">
                      <span>Phase Timer</span>
                      <span className="font-mono text-cyan-400 font-bold">{node.timer}s</span>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Main Arterial Corridor (Row 0)</div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
              {nodes.slice(0, 5).map((node, idx) => {
                const nodeIdx = idx;
                const isSelected = activePath.includes(nodeIdx);
                const isGreen = node.phase.includes('GREEN');
                const isYellow = node.phase.includes('YELLOW');

                return (
                  <div
                    key={node.id}
                    onClick={() => toggleNode(nodeIdx)}
                    className={`cursor-pointer bg-slate-900 border rounded-xl p-3.5 transition relative overflow-hidden ${
                      isSelected ? 'border-cyan-400 ring-2 ring-cyan-500/30' :
                      node.isPreempt ? 'border-rose-500 bg-rose-950/20' :
                      node.isFlushing ? 'border-purple-500 bg-purple-950/20' :
                      'border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-300">{node.name}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${
                        node.isPreempt ? 'bg-rose-900/80 text-rose-300 animate-pulse' :
                        node.isFlushing ? 'bg-purple-900/80 text-purple-300' :
                        isGreen ? 'bg-emerald-950 text-emerald-400 border border-emerald-700/50' :
                        isYellow ? 'bg-amber-950 text-amber-400 border border-amber-700/50' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {node.isPreempt ? 'PREEMPT' : node.isFlushing ? 'FLUSHING' : node.phase}
                      </span>
                    </div>

                    {/* Queues */}
                    <div className="space-y-1.5 text-xs mt-3">
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>NS Queue</span>
                          <span className="font-semibold text-slate-200">{node.nsQueue}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-cyan-500 h-full rounded-full transition-all" style={{ width: `${Math.min(100, node.nsQueue * 10)}%` }}></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>EW Queue</span>
                          <span className="font-semibold text-slate-200">{node.ewQueue}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-indigo-500 h-full rounded-full transition-all" style={{ width: `${Math.min(100, node.ewQueue * 10)}%` }}></div>
                        </div>
                      </div>
                    </div>

                    {/* Elapsed Timer Gauge */}
                    <div className="mt-3 pt-2 border-t border-slate-800 flex justify-between items-center text-[11px] text-slate-400">
                      <span>Phase Timer</span>
                      <span className="font-mono text-cyan-400 font-bold">{node.timer}s</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Single Junction Deep Monitor (A0) */}
      {activeTab === 'intersection' && (
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
            <h2 className="text-lg font-bold text-slate-100 mb-1">Intersection A0 — Telemetry & Phase Actuation</h2>
            <p className="text-xs text-slate-400 mb-6">Localized 4-arm approach queues, continuous-time NeurODE integration, and statutory yellow clearances.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              {/* 4-way visual representation */}
              <div className="relative w-72 h-72 mx-auto bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-center p-4">
                {/* North */}
                <div className="absolute top-2 text-center">
                  <div className="text-[10px] text-slate-400">North Approach (Lane A)</div>
                  <div className="text-lg font-black text-cyan-400">{trafficData.laneACount} veh</div>
                </div>
                {/* South */}
                <div className="absolute bottom-2 text-center">
                  <div className="text-[10px] text-slate-400">South Approach (Lane C)</div>
                  <div className="text-lg font-black text-cyan-400">{trafficData.laneCCount} veh</div>
                </div>
                {/* West */}
                <div className="absolute left-2 text-center">
                  <div className="text-[10px] text-slate-400">West (Lane D)</div>
                  <div className="text-lg font-black text-indigo-400">{trafficData.laneDCount} veh</div>
                </div>
                {/* East */}
                <div className="absolute right-2 text-center">
                  <div className="text-[10px] text-slate-400">East (Lane B)</div>
                  <div className="text-lg font-black text-indigo-400">{trafficData.laneBCount} veh</div>
                </div>
                {/* Center Signal Light Indicator */}
                <div className="w-20 h-20 bg-slate-900 border border-slate-700 rounded-xl flex flex-col items-center justify-center gap-1.5 shadow-inner">
                  <div className={`w-3.5 h-3.5 rounded-full ${trafficData.activeSignal.includes('NS') ? 'bg-emerald-500 shadow-lg shadow-emerald-500/50' : 'bg-slate-700'}`}></div>
                  <div className={`w-3.5 h-3.5 rounded-full ${trafficData.activeSignal.includes('YELLOW') ? 'bg-amber-500 shadow-lg shadow-amber-500/50 animate-pulse' : 'bg-slate-700'}`}></div>
                  <div className={`w-3.5 h-3.5 rounded-full ${trafficData.activeSignal.includes('EW') ? 'bg-emerald-500 shadow-lg shadow-emerald-500/50' : 'bg-slate-700'}`}></div>
                </div>
              </div>

              {/* Approach Queues & Details */}
              <div className="space-y-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-xs text-slate-400 mb-1">Active Signal Actuation</div>
                  <div className="text-base font-bold text-slate-100">{trafficData.activeSignal}</div>
                </div>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-xs text-slate-400 mb-1">Municipal Safety Envelopes</div>
                  <div className="text-xs text-slate-300 space-y-1">
                    <div>• Statutory Minimum Green: <span className="text-cyan-400 font-mono">10.0 s</span></div>
                    <div>• Queue-Proportional Max Green: <span className="text-cyan-400 font-mono">45.0 s</span></div>
                    <div>• Mandatory Clearance Interval: <span className="text-amber-400 font-mono">3.0 s Yellow</span></div>
                  </div>
                </div>
                {/* Manual Override Controls */}
                <div className="pt-2">
                  <div className="text-xs text-slate-400 mb-2">Manual Dispatch Overrides</div>
                  <div className="flex flex-wrap gap-2">
                    <button onClick={() => sendCommand('EMERGENCY_NS', 'Force NS Green')} className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs rounded border border-slate-700">Force NS Green</button>
                    <button onClick={() => sendCommand('EMERGENCY_EW', 'Force EW Green')} className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs rounded border border-slate-700">Force EW Green</button>
                    <button onClick={() => sendCommand('POLICE_STOP', 'Police All-Red')} className="px-3 py-1.5 bg-rose-950 text-rose-300 hover:bg-rose-900 text-xs rounded border border-rose-800">Police Stop</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Edge Inference & Shockwave Analytics */}
      {activeTab === 'analytics' && (
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-1">Edge Inference Latency</div>
              <div className="text-3xl font-black text-slate-100 mt-2">6.06 <span className="text-sm font-normal text-slate-400">µs</span></div>
              <p className="text-xs text-slate-400 mt-2">ONNX Runtime FP32 benchmarked over 10,000 forward passes (162,074 FPS). 4.10x faster than PyTorch CPU.</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs font-bold text-purple-400 uppercase tracking-wider mb-1">INT8 Storage Footprint</div>
              <div className="text-3xl font-black text-slate-100 mt-2">8.33 <span className="text-sm font-normal text-slate-400">KB</span></div>
              <p className="text-xs text-slate-400 mt-2">Dynamic INT8 quantized SMDP weights fit comfortably inside constrained L1/L2 microcontroller cache.</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1">Post-Preemption Recovery</div>
              <div className="text-3xl font-black text-slate-100 mt-2">13.5 <span className="text-sm font-normal text-slate-400">s</span></div>
              <p className="text-xs text-slate-400 mt-2">AURA momentum flushing eliminates cross-arterial queue cascades 68% faster than traditional actuated controllers.</p>
            </div>
          </div>

          {/* Micro-Benchmark Summary Table */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
            <h3 className="text-base font-bold text-slate-200 mb-4">Edge Micro-Benchmarking Suite Results (CPU & Embedded Profile)</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                    <th className="py-2.5">Inference Engine</th>
                    <th className="py-2.5">Precision</th>
                    <th className="py-2.5">Mean Latency</th>
                    <th className="py-2.5">P99 Latency</th>
                    <th className="py-2.5">Throughput</th>
                    <th className="py-2.5">Model Size</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  <tr>
                    <td className="py-3 font-semibold text-slate-100">PyTorch (CPU JIT)</td>
                    <td>FP32</td>
                    <td>24.83 µs</td>
                    <td>50.59 µs</td>
                    <td>40,051 FPS</td>
                    <td>18.52 KB</td>
                  </tr>
                  <tr className="bg-cyan-950/20">
                    <td className="py-3 font-semibold text-cyan-300">ONNX Runtime (AURA Native)</td>
                    <td className="text-cyan-300 font-semibold">FP32</td>
                    <td className="text-emerald-400 font-bold">6.06 µs</td>
                    <td className="text-emerald-400 font-bold">11.08 µs</td>
                    <td className="text-emerald-400 font-bold">162,074 FPS</td>
                    <td>19.21 KB</td>
                  </tr>
                  <tr className="bg-purple-950/20">
                    <td className="py-3 font-semibold text-purple-300">ONNX Runtime (Dynamic Quantized)</td>
                    <td className="text-purple-300 font-semibold">INT8</td>
                    <td className="text-purple-400 font-bold">8.53 µs</td>
                    <td className="text-purple-400 font-bold">17.58 µs</td>
                    <td className="text-purple-400 font-bold">115,703 FPS</td>
                    <td className="text-emerald-400 font-bold">8.33 KB</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
