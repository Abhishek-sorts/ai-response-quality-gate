import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Clock, ShieldAlert } from 'lucide-react';

export default function DebuggerDashboard({ data }) {
  const { success, final_response, trace, total_latency_ms, recovery_strategy_used, retry_count } = data;

  return (
    <div className="glass-panel" style={{ marginTop: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center' }}>
          Execution Trace
          {success ? (
            <span style={{ marginLeft: '1rem', color: 'var(--success-color)', display: 'flex', alignItems: 'center', fontSize: '1rem' }}>
              <CheckCircle size={18} style={{ marginRight: '4px' }} /> SUCCESS
            </span>
          ) : (
            <span style={{ marginLeft: '1rem', color: 'var(--danger-color)', display: 'flex', alignItems: 'center', fontSize: '1rem' }}>
              <XCircle size={18} style={{ marginRight: '4px' }} /> FAILED
            </span>
          )}
        </h2>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div className="badge latency" style={{ margin: 0 }}>
             Retries: {retry_count}
          </div>
          <div className="badge latency" style={{ margin: 0 }}>
            <Clock size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }}/> {total_latency_ms}ms total
          </div>
        </div>
      </div>

      {recovery_strategy_used && (
        <div style={{ background: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.3)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
          <ShieldAlert style={{ color: '#c084fc', marginRight: '1rem' }} />
          <div>
            <div style={{ fontWeight: 600, color: '#c084fc' }}>Auto-Recovery Engaged</div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Strategy Used: {recovery_strategy_used}</div>
          </div>
        </div>
      )}

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Attempts History</h3>
        {trace.map((step, index) => (
          <div key={index} className={`trace-step ${step.error ? 'error' : 'success'}`}>
            <div style={{ marginBottom: '0.5rem' }}>
              <span className="badge">Attempt {step.attempt}</span>
              <span className="badge model">{step.model_used}</span>
              <span className="badge latency">{step.latency_ms}ms</span>
              {step.error ? <span className="badge error">Failed</span> : <span className="badge success">Valid</span>}
              {step.failure_type && <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: '1px solid rgba(239, 68, 68, 0.4)' }}>{step.failure_type}</span>}
              {step.repair_applied && <span className="badge" style={{ background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc', border: '1px solid rgba(168, 85, 247, 0.4)' }}>Response Repair Applied</span>}
              {step.final_validation && <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' }}>Final Validation</span>}
            </div>
            
            {step.error && (
              <div style={{ color: 'var(--danger-color)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center' }}>
                <AlertTriangle size={14} style={{ marginRight: '4px' }} /> {step.error}
              </div>
            )}
            
            {step.validation_result && step.validation_result.issues && step.validation_result.issues.length > 0 && (
               <div style={{ color: 'var(--warning-color)', fontSize: '0.875rem', marginBottom: '0.5rem', background: 'rgba(245, 158, 11, 0.1)', padding: '0.5rem', borderRadius: '4px' }}>
                 <strong>Issues Detected:</strong>
                 <ul style={{ marginLeft: '1.5rem', marginTop: '0.25rem' }}>
                    {step.validation_result.issues.map((issue, i) => <li key={i}>{issue}</li>)}
                 </ul>
               </div>
            )}

            {step.validation_result && step.validation_result.recommended_action && (
               <div style={{ color: '#3b82f6', fontSize: '0.875rem', marginBottom: '0.5rem', background: 'rgba(59, 130, 246, 0.1)', padding: '0.5rem', borderRadius: '4px' }}>
                 <strong>Recommended Action:</strong> {step.validation_result.recommended_action}
               </div>
            )}


            {step.validation_result && step.validation_result.is_valid !== null && (
              <div className="dashboard-grid" style={{ marginTop: '1rem', marginBottom: '1rem' }}>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px' }}>
                  <div className="metric-row">
                    <span className="metric-label">Quality Score</span>
                    <span className="metric-value" style={{ color: step.validation_result.quality_score > 0.7 ? 'var(--success-color)' : 'var(--warning-color)' }}>{step.validation_result.quality_score.toFixed(2)}</span>
                  </div>
                  <div className="metric-row">
                    <span className="metric-label">Grounding</span>
                    <span className="metric-value">{step.validation_result.grounding_score.toFixed(2)}</span>
                  </div>
                  <div className="metric-row">
                    <span className="metric-label">Completeness</span>
                    <span className="metric-value">{step.validation_result.completeness_score.toFixed(2)}</span>
                  </div>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px' }}>
                  <div className="metric-row">
                    <span className="metric-label">Hallucination</span>
                    <span className="metric-value" style={{ color: step.validation_result.hallucination_score > 0.3 ? 'var(--danger-color)' : 'var(--success-color)' }}>{step.validation_result.hallucination_score.toFixed(2)}</span>
                  </div>
                  <div className="metric-row">
                    <span className="metric-label">Contradiction</span>
                    <span className="metric-value">{step.validation_result.contradiction_score.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}

            <div style={{ marginTop: '0.5rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Raw Model Output:</div>
              <pre>{step.raw_response.slice(0, 500)}{step.raw_response.length > 500 ? '...' : ''}</pre>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Final Recovered Response</h3>
        {final_response ? (
          <pre style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#a7f3d0' }}>
            {JSON.stringify(final_response, null, 2)}
          </pre>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No valid response could be recovered.</div>
        )}
      </div>
    </div>
  );
}
