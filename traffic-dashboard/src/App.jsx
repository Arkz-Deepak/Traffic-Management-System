import { useState, useEffect } from 'react';

function App() {
  const [activeTab, setActiveTab] = useState('intersection'); // 'intersection' or 'tactical'
  
  // Phase 1: Real-time traffic telemetry
  const [trafficData, setTrafficData] = useState({
    laneACount: 0,
    laneBCount: 0,
    laneCCount: 0,
    laneDCount: 0,
    activeSignal: 'Connecting to Server...',
    systemStatus: 'Automated AI Control',
    systemMode: 'AI_OPTIMIZED',
    isAiActive: false
  });

  // Phase 2: Tactical Dispatch state (5x2 Grid)
  const [activePath, setActivePath] = useState([]);
  const [dispatchStatus, setDispatchStatus] = useState('Standby');
  const intersections = Array.from({ length: 10 }, (_, i) => i);

  // Polling Interval: 500ms sync with backend Single Source of Truth
  useEffect(() => {
    const fetchTrafficData = async () => {
      try {
        const response = await fetch('http://localhost:3000/api/traffic');
        if (response.ok) {
          const data = await response.json();
          setTrafficData(data);
        }
      } catch (error) {
        // Backend offline
      }
    };

    const interval = setInterval(fetchTrafficData, 500);
    return () => clearInterval(interval);
  }, []);

  // Send manual override to backend
  const sendCommand = async (commandType, displayName) => {
    try {
      await fetch('http://localhost:3000/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: commandType, displayName: displayName })
      });
    } catch (error) {
      console.error("Failed to send command:", error);
    }
  };

  // Phase 2: Toggle node in tactical path
  const toggleNode = (nodeId) => {
    if (activePath.includes(nodeId)) {
      const index = activePath.indexOf(nodeId);
      setActivePath(activePath.slice(0, index));
    } else {
      setActivePath([...activePath, nodeId]);
    }
  };

  // Phase 2: Dispatch ambulance route to backend (bridges to ROS 2 DDS)
  const dispatchAmbulance = async () => {
    if (activePath.length === 0) return;
    setDispatchStatus('Dispatching...');
    try {
      const res = await fetch('http://localhost:3000/api/dispatch-ambulance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ route: activePath })
      });
      if (res.ok) {
        const result = await res.json();
        setDispatchStatus(result.message || 'Green Wave Active');
        setTimeout(() => {
          setActivePath([]);
          setDispatchStatus('Standby');
        }, 6000);
      } else {
        setDispatchStatus('Dispatch Failed');
      }
    } catch (error) {
      console.error("Failed to bridge ambulance path:", error);
      setDispatchStatus('Comm Failure');
    }
  };

  const getStatusText = () => {
    if (!trafficData.isAiActive && trafficData.systemMode === 'AI_OPTIMIZED') {
      return "AI Agent Offline - Waiting for Simulation...";
    }
    return trafficData.activeSignal;
  };

  return (
    <div className="min-h-screen bg-slate-100 p-6 md:p-8 font-sans text-slate-800">
      {/* Header */}
      <header className="mb-8 text-center max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
          <div className="text-left">
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">
              🚦 AURA: Smart Traffic Management System
            </h1>
            <p className="text-sm text-slate-500 font-medium mt-1">
              Deep Reinforcement Learning (DQN) + Multi-Agent ROS 2 Preemption Architecture
            </p>
          </div>
          
          {/* Dynamic Status Badge */}
          <div className="flex items-center gap-3">
            <span className={`px-4 py-2 rounded-full font-bold text-sm text-white shadow-sm transition-all duration-300 ${
              trafficData.isAiActive ? 'bg-emerald-600' : 'bg-red-600 animate-pulse'
            }`}>
              {trafficData.isAiActive ? '● AI Agent Connected' : '○ AI Agent Offline'}
            </span>
            <span className="px-4 py-2 rounded-full font-bold text-sm bg-slate-800 text-white shadow-sm">
              Mode: {trafficData.systemMode === 'AI_OPTIMIZED' ? 'AI Managed' : trafficData.systemMode}
            </span>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex justify-center border-b border-slate-200">
          <button
            onClick={() => setActiveTab('intersection')}
            className={`py-3 px-6 font-bold text-sm md:text-base border-b-2 transition-colors ${
              activeTab === 'intersection'
                ? 'border-emerald-600 text-emerald-600 bg-emerald-50/50'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            📊 Intersection A0 Live Monitor (Phase 1)
          </button>
          <button
            onClick={() => setActiveTab('tactical')}
            className={`py-3 px-6 font-bold text-sm md:text-base border-b-2 transition-colors ${
              activeTab === 'tactical'
                ? 'border-red-600 text-red-600 bg-red-50/50'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            🚨 Tactical Dispatch & Green Wave (Phase 2 Grid)
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      {activeTab === 'intersection' ? (
        <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Video Feed Section */}
          <section className="col-span-1 lg:col-span-2 bg-white p-6 rounded-xl shadow-md border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-slate-700">Live CCTV Telemetry (SUMO Micro-Simulation)</h2>
              <span className="text-xs bg-slate-100 text-slate-600 px-3 py-1 rounded-full font-semibold border border-slate-300">
                Intersection: A0
              </span>
            </div>
            <div className="bg-slate-900 h-[480px] rounded-lg flex items-center justify-center text-slate-400 border-4 border-slate-800 relative overflow-hidden">
              <div className="text-center z-10 p-6">
                <div className="text-5xl mb-4">📹</div>
                <p className="font-mono text-lg font-bold text-slate-200">YOLOv11 Real-Time Inference Stream</p>
                <p className="text-xs text-slate-400 mt-2 max-w-md mx-auto">
                  Edge perception engine tracks vehicle bounding boxes across approaching corridors (North, East, South, West)
                </p>
              </div>

              {trafficData.isAiActive && (
                <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/60 px-3 py-1.5 rounded-full border border-emerald-500/30">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                  </span>
                  <span className="text-emerald-400 text-xs font-bold tracking-wider">LIVE RL AGENT</span>
                </div>
              )}
            </div>
          </section>

          {/* Analytics & Signal Status Section */}
          <section className="col-span-1 flex flex-col gap-6">
            <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200">
              <h2 className="text-xl font-bold mb-4 text-slate-700">Live Queue Lengths (Vehicles)</h2>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { name: 'Lane A (North)', count: trafficData.laneACount, icon: '⬆️' },
                  { name: 'Lane B (East)', count: trafficData.laneBCount, icon: '➡️' },
                  { name: 'Lane C (South)', count: trafficData.laneCCount, icon: '⬇️' },
                  { name: 'Lane D (West)', count: trafficData.laneDCount, icon: '⬅️' },
                ].map(lane => (
                  <div key={lane.name} className="bg-slate-50 p-4 rounded-lg border border-slate-200 flex flex-col items-center text-center">
                    <span className="text-lg mb-1">{lane.icon}</span>
                    <h3 className="font-semibold text-slate-600 text-xs">{lane.name}</h3>
                    <span className="text-3xl font-black text-slate-900 mt-1">{lane.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200 text-center flex-grow flex flex-col justify-center">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Active Signal Phase</h3>
              <p className={`text-xl font-black p-4 rounded-lg border-2 transition-all duration-300 ${
                trafficData.isAiActive
                  ? 'border-emerald-500 text-emerald-700 bg-emerald-50'
                  : 'border-amber-400 text-amber-700 bg-amber-50'
              }`}>
                {getStatusText()}
              </p>
            </div>
          </section>

          {/* Overrides Section */}
          <section className="col-span-1 lg:col-span-3 bg-white p-6 rounded-xl shadow-md border border-slate-200 flex flex-col items-center gap-6">
            <div className="w-full max-w-4xl bg-red-50 border-2 border-red-200 rounded-xl p-5">
              <h3 className="text-red-800 font-bold text-center mb-3 text-sm uppercase tracking-wider">
                🚨 Emergency Vehicle Priority Override (Instant Preemption)
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  onClick={() => sendCommand('EMERGENCY_NS', 'North')}
                  className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg shadow-sm transition active:scale-95"
                >
                  Clear North (N/S)
                </button>
                <button
                  onClick={() => sendCommand('EMERGENCY_EW', 'East')}
                  className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg shadow-sm transition active:scale-95"
                >
                  Clear East (E/W)
                </button>
                <button
                  onClick={() => sendCommand('EMERGENCY_NS', 'South')}
                  className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg shadow-sm transition active:scale-95"
                >
                  Clear South (N/S)
                </button>
                <button
                  onClick={() => sendCommand('EMERGENCY_EW', 'West')}
                  className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg shadow-sm transition active:scale-95"
                >
                  Clear West (E/W)
                </button>
              </div>
            </div>

            <div className="flex flex-wrap justify-center gap-4">
              <button
                onClick={() => sendCommand('POLICE_STOP', 'Global')}
                className="px-8 py-3 bg-amber-400 hover:bg-amber-500 text-slate-900 font-bold rounded-lg shadow-sm transition flex items-center gap-2 active:scale-95"
              >
                👮 Police All-Stop (Manual Red)
              </button>
              <button
                onClick={() => sendCommand('AI_OPTIMIZED', 'Global')}
                className="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg shadow-sm transition flex items-center gap-2 active:scale-95"
              >
                🔄 Resume AI Optimization
              </button>
            </div>
          </section>
        </main>
      ) : (
        /* Tactical Dispatch Section (Phase 2 MARL 5x2 Grid) */
        <main className="max-w-5xl mx-auto bg-slate-900 text-white p-8 rounded-2xl shadow-xl border border-slate-800">
          <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-800">
            <div>
              <h2 className="text-2xl font-black text-blue-400">🚑 AURA Tactical Dispatch Command</h2>
              <p className="text-sm text-slate-400 mt-1">
                Multi-Agent Green Wave Trajectory Preemption across 10-Intersection SUMO Grid
              </p>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400 block mb-1">DDS Dispatch Status</span>
              <span className={`px-4 py-1.5 rounded-full text-xs font-bold ${
                dispatchStatus.includes('Active') || dispatchStatus.includes('Initiated')
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                  : 'bg-slate-800 text-slate-300'
              }`}>
                {dispatchStatus}
              </span>
            </div>
          </div>

          <p className="text-sm text-slate-300 mb-6">
            Click intersection nodes to construct the emergency route polyline. When dispatched, the route is broadcasted over ROS 2 DDS to force sequential green waves.
          </p>

          {/* 5x2 Grid Map */}
          <div className="grid grid-cols-5 gap-4 bg-slate-950 p-6 rounded-xl border border-slate-800 mb-6">
            {intersections.map(node => {
              const isSelected = activePath.includes(node);
              const pathIndex = activePath.indexOf(node);
              return (
                <button
                  key={node}
                  onClick={() => toggleNode(node)}
                  className={`h-24 rounded-xl font-bold flex flex-col items-center justify-center transition-all ${
                    isSelected
                      ? 'bg-red-900/80 border-2 border-red-500 shadow-lg shadow-red-500/30 text-white scale-105'
                      : 'bg-slate-850 hover:bg-slate-800 border border-slate-700 text-slate-300'
                  }`}
                >
                  <span className="text-lg">Int {node}</span>
                  {isSelected && (
                    <span className="text-xs text-red-300 font-semibold mt-1">
                      Step {pathIndex + 1}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Path Display & Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
            <div className="text-sm">
              <span className="text-slate-400">Constructed Route: </span>
              <span className="font-mono font-bold text-amber-400">
                {activePath.length > 0 ? activePath.map(n => `Int ${n}`).join(' ➔ ') : 'None selected'}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setActivePath([])}
                className="px-4 py-2.5 rounded-lg border border-slate-600 text-slate-300 hover:bg-slate-700 text-sm font-semibold transition"
              >
                Clear Route
              </button>
              <button
                onClick={dispatchAmbulance}
                disabled={activePath.length === 0 || dispatchStatus === 'Dispatching...'}
                className={`px-6 py-2.5 rounded-lg font-bold text-sm shadow-md transition ${
                  activePath.length > 0
                    ? 'bg-red-600 hover:bg-red-700 text-white cursor-pointer active:scale-95'
                    : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                }`}
              >
                ⚡ Force Green Wave Route
              </button>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}

export default App;
