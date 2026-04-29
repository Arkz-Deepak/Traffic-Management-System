import { useState, useEffect } from 'react';

function App() {
  // Combine traffic metrics into a single state object for clean backend fetching
  const [trafficData, setTrafficData] = useState({
    laneACount: 0,
    laneBCount: 0,
    laneCCount: 0,
    laneDCount: 0,
    activeSignal: 'Connecting to Server...',
    systemStatus: 'Automated AI Control', // Controlled by Backend
    isAiActive: false // Controlled by Backend Watchdog
  });

  // Polling Interval: Keeps dashboard in sync with the actual AI simulation
  // Set to 500ms for a "Live" feel during the pitch
  useEffect(() => {
    const fetchTrafficData = async () => {
      try {
        const response = await fetch('http://localhost:3000/api/traffic');
        const data = await response.json();
        
        // Update all metrics regardless of mode so numbers don't freeze
        setTrafficData(data);
      } catch (error) {
        console.error("Backend unreachable:", error);
      }
    };

    const interval = setInterval(fetchTrafficData, 500);
    return () => clearInterval(interval);
  }, []); 

  // --- NEW: Command Function sends manual overrides to Backend ---
  const sendCommand = async (commandType, displayName) => {
    try {
      await fetch('http://localhost:3000/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: commandType, displayName: displayName })
      });
      // Do not update local state here. Wait for the next poll to get 
      // confirmation from the backend Single Source of Truth.
    } catch (error) {
      console.error("Failed to send command:", error);
    }
  };

  // Maps backend modes to friendly frontend display names
  const getStatusText = () => {
    if (!trafficData.isAiActive && trafficData.systemMode === 'AI_OPTIMIZED') return "AI Agent Offline";
    return trafficData.activeSignal;
  }

  return (
    <div className="min-h-screen bg-slate-100 p-8 font-sans text-slate-800">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 mb-4">
          Smart Traffic Management System
        </h1>
        {/* Dynamic Status Badge controlled by Backend Single Source of Truth */}
        <span className={`px-4 py-2 rounded-full font-bold text-white shadow-sm transition-colors duration-300
          ${trafficData.isAiActive ? 'bg-slate-800' : 'bg-red-600 animate-pulse'}`}>
          Mode: {trafficData.systemMode === 'AI_OPTIMIZED' ? 'AI Managed' : trafficData.systemMode}
        </span>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Video Feed Section */}
        <section className="col-span-1 lg:col-span-2 bg-white p-6 rounded-xl shadow-md border border-slate-200">
          <h2 className="text-xl font-bold mb-4 text-slate-700">Live CCTV Feed (SUMO Integration)</h2>
          <div className="bg-slate-900 h-[500px] rounded-lg flex items-center justify-center text-slate-400 border-4 border-slate-800 relative overflow-hidden">
            <p className="font-mono z-10">YOLOv8 Real-time Inference Feed</p>
            {/* Visual indicator that AI is actually running on the feed */}
            {trafficData.isAiActive && (
                 <div className="absolute top-2 right-2 flex items-center gap-2 bg-black/50 p-2 rounded">
                    <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                    </span>
                    <span className="text-emerald-400 text-xs font-bold">LIVE AI</span>
                 </div>
            )}
          </div>
        </section>

        {/* Analytics Section */}
        <section className="col-span-1 flex flex-col gap-4">
          <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200">
            <h2 className="text-xl font-bold mb-4 text-slate-700">Live Traffic Metrics (Queue Length)</h2>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
                {[
                    {name: 'Lane A (North)', count: trafficData.laneACount},
                    {name: 'Lane B (East)', count: trafficData.laneBCount},
                    {name: 'Lane C (South)', count: trafficData.laneCCount},
                    {name: 'Lane D (West)', count: trafficData.laneDCount},
                ].map(lane => (
                    <div key={lane.name} className="bg-slate-50 p-4 rounded-lg border border-slate-100 flex flex-col items-center text-center">
                      <h3 className="font-semibold text-slate-600 text-sm">{lane.name}</h3>
                      <span className="text-3xl font-black text-slate-800">{lane.count}</span>
                    </div>
                ))}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200 text-center flex-grow flex flex-col justify-center">
             <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Active Intersection Status</h3>
             {/* Changes color based on whether AI is active or emergency mode is engaged */}
             <p className={`text-2xl font-black p-3 rounded-lg border-2 transition-all duration-300
               ${trafficData.isAiActive ? 'border-emerald-500 text-emerald-600 bg-emerald-50' : 'border-red-500 text-red-600 bg-red-50'}`}>
               {getStatusText()}
             </p>
          </div>
        </section>

        {/* Overrides Section - Sends Commands to Backend */}
        <section className="col-span-1 lg:col-span-3 bg-white p-6 rounded-xl shadow-md border border-slate-200 flex flex-col items-center gap-6">
          
          {/* Emergency Routing Panel */}
          <div className="w-full max-w-3xl bg-red-50 border-2 border-red-200 rounded-xl p-5">
             <h3 className="text-red-800 font-bold text-center mb-4 text-sm uppercase tracking-wider">🚨 Emergency Vehicle Priority Override</h3>
             <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button onClick={() => sendCommand('EMERGENCY_NS', 'North')} className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-4 rounded shadow-sm transition">Clear North</button>
                <button onClick={() => sendCommand('EMERGENCY_EW', 'East')} className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-4 rounded shadow-sm transition">Clear East</button>
                <button onClick={() => sendCommand('EMERGENCY_NS', 'South')} className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-4 rounded shadow-sm transition">Clear South</button>
                <button onClick={() => sendCommand('EMERGENCY_EW', 'West')} className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-4 rounded shadow-sm transition">Clear West</button>
             </div>
          </div>

          {/* Manual Controls */}
          <div className="flex flex-wrap justify-center gap-4">
            <button 
              onClick={() => sendCommand('POLICE_STOP')} 
              className="px-8 py-3 bg-amber-400 hover:bg-amber-500 text-slate-900 font-bold rounded-lg shadow-sm transition-colors flex items-center gap-2">
              👮 Police All-Stop (Manual)
            </button>
            <button 
              onClick={() => sendCommand('AI_OPTIMIZED')} 
              className="px-8 py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-lg shadow-sm transition-colors flex items-center gap-2">
              🔄 Resume AI Optimization
            </button>
          </div>

        </section>
      </main>
    </div>
  );
}

export default App;