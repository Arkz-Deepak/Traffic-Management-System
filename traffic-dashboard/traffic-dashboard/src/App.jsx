import React, { useState } from 'react';
import axios from 'axios';
import { AlertTriangle, Send, XCircle } from 'lucide-react';
import './App.css'; // Make sure you have basic styling

const App = () => {
  const [activePath, setActivePath] = useState([]);
  const [dispatchStatus, setDispatchStatus] = useState('Standby');

  // Generate a 5x2 grid to match your SUMO network
  const intersections = Array.from({ length: 10 }, (_, i) => i);

  // Handle clicking an intersection on the map
  const toggleNode = (nodeId) => {
    if (activePath.includes(nodeId)) {
      // If already selected, remove it and everything after it (like undoing a line)
      const index = activePath.indexOf(nodeId);
      setActivePath(activePath.slice(0, index));
    } else {
      // Add node to the path
      setActivePath([...activePath, nodeId]);
    }
  };

  // Blast the payload to your Node.js Bridge
  const dispatchAmbulance = async () => {
    if (activePath.length === 0) return;
    
    setDispatchStatus('Dispatching...');
    try {
      // Point this to your Node.js server port
      await axios.post('http://localhost:3000/api/dispatch-ambulance', {
        route: activePath
      });
      setDispatchStatus('Green Wave Active');
      
      // Reset the UI after 5 seconds
      setTimeout(() => {
        setActivePath([]);
        setDispatchStatus('Standby');
      }, 5000);
      
    } catch (error) {
      console.error("Failed to bridge to ROS 2:", error);
      setDispatchStatus('Comm Failure');
    }
  };

  return (
    <div className="dashboard-container" style={{ padding: '2rem', fontFamily: 'sans-serif', backgroundColor: '#1a1a1a', color: 'white', minHeight: '100vh' }}>
      
      <header style={{ borderBottom: '1px solid #333', paddingBottom: '1rem', marginBottom: '2rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#60a5fa' }}>
          <AlertTriangle color="#ef4444" /> AURA Tactical Dispatch Command
        </h1>
        <p>System Status: <span style={{ color: dispatchStatus === 'Green Wave Active' ? '#22c55e' : '#9ca3af' }}>{dispatchStatus}</span></p>
      </header>

      {/* The Interactive Topological Map */}
      <div className="grid-map" style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(5, 1fr)', 
        gap: '2rem', 
        background: '#262626', 
        padding: '3rem', 
        borderRadius: '12px',
        border: '1px solid #404040'
      }}>
        {intersections.map((node) => {
          const isSelected = activePath.includes(node);
          const pathIndex = activePath.indexOf(node);
          
          return (
            <button
              key={node}
              onClick={() => toggleNode(node)}
              style={{
                height: '80px',
                borderRadius: '50%',
                border: `3px solid ${isSelected ? '#ef4444' : '#4b5563'}`,
                backgroundColor: isSelected ? '#7f1d1d' : '#171717',
                color: 'white',
                fontSize: '1.2rem',
                fontWeight: 'bold',
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: isSelected ? '0 0 15px rgba(239, 68, 68, 0.5)' : 'none'
              }}
            >
              Int {node}
              {isSelected && <div style={{ fontSize: '0.8rem', color: '#fca5a5' }}>Step {pathIndex + 1}</div>}
            </button>
          );
        })}
      </div>

      {/* Control Panel */}
      <div className="controls" style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
        <button 
          onClick={dispatchAmbulance}
          disabled={activePath.length === 0 || dispatchStatus === 'Dispatching...'}
          style={{
            padding: '1rem 2rem',
            backgroundColor: activePath.length > 0 ? '#ef4444' : '#374151',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            cursor: activePath.length > 0 ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}
        >
          <Send size={20} /> Force Green Wave Route
        </button>
        
        <button 
          onClick={() => setActivePath([])}
          style={{
            padding: '1rem',
            backgroundColor: 'transparent',
            color: '#9ca3af',
            border: '1px solid #4b5563',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '5px'
          }}
        >
          <XCircle size={20} /> Clear Map
        </button>
      </div>

    </div>
  );
};

export default App;