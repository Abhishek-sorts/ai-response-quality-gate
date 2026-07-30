import React, { useState } from 'react';
import axios from 'axios';
import ExecutionForm from './components/ExecutionForm';
import DebuggerDashboard from './components/DebuggerDashboard';
import { Activity } from 'lucide-react';
import './index.css';

const API_BASE = 'http://127.0.0.1:8000/api';

function App() {
  const [executionResult, setExecutionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleExecute = async (payload) => {
    setLoading(true);
    setError(null);
    setExecutionResult(null);
    try {
      let schemaObj = {};
      try {
        schemaObj = JSON.parse(payload.expected_schema);
      } catch (e) {
        throw new Error("Invalid JSON in Expected Schema");
      }

      const requestBody = {
        prompt: payload.prompt,
        context: payload.context,
        expected_schema: schemaObj
      };

      const res = await axios.post(`${API_BASE}/execute`, requestBody);
      setExecutionResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1><Activity className="inline-block mr-2" size={32} style={{verticalAlign: 'bottom'}} /> AI Response Quality Gate</h1>
        <p style={{ color: 'var(--text-muted)' }}>Execution Debugger & Auto-Healing Pipeline</p>
      </header>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
        <div className="glass-panel">
          <ExecutionForm onSubmit={handleExecute} loading={loading} />
          {error && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--danger-color)', borderRadius: '8px', color: 'var(--danger-color)' }}>
              {error}
            </div>
          )}
        </div>
        
        {executionResult && (
          <DebuggerDashboard data={executionResult} />
        )}
      </div>
    </div>
  );
}

export default App;
