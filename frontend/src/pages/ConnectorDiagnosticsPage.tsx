import { useCallback } from 'react'

import { getConnectorDiagnostics } from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

export function ConnectorDiagnosticsPage() {
  const diagnostics = useAsyncData(useCallback(() => getConnectorDiagnostics(), []), [])

  const getPlatformIcon = (platform: string) => {
    // Simple placeholder icon letters or styles
    const styles: Record<string, { bg: string, color: string }> = {
      wordpress: { bg: '#e0f2fe', color: '#0284c7' },
      hubspot: { bg: '#ffedd5', color: '#ea580c' },
      linkedin: { bg: '#eff6ff', color: '#2563eb' },
      meta: { bg: '#fae8ff', color: '#c084fc' },
      ga4: { bg: '#ecfdf5', color: '#059669' },
    }
    const style = styles[platform.toLowerCase()] || { bg: '#f1f5f9', color: '#475569' }
    return (
      <div style={{
        width: '40px',
        height: '40px',
        borderRadius: '8px',
        backgroundColor: style.bg,
        color: style.color,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        fontSize: '1.2rem',
        textTransform: 'uppercase',
      }}>
        {platform.substring(0, 2)}
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h2>Connector Diagnostics</h2>
        <p>Monitor the configuration and health state of your external publishing integrations.</p>
      </div>

      {diagnostics.loading && <p style={{ color: 'var(--text-muted)' }}>Loading connectors...</p>}
      {diagnostics.error && <p className="badge danger">{diagnostics.error}</p>}
      
      {!diagnostics.loading && !diagnostics.error && (diagnostics.data ?? []).length === 0 && (
        <div className="panel">
          <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No connector diagnostics available.</p>
        </div>
      )}

      {!diagnostics.loading && !diagnostics.error && (diagnostics.data ?? []).length > 0 && (
        <div className="grid-cols-2">
          {(diagnostics.data ?? []).map((connector) => (
            <div key={connector.platform} className="panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem', minHeight: '180px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                  {getPlatformIcon(connector.platform)}
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.1rem', textTransform: 'capitalize' }}>{connector.platform}</h3>
                    <span className="row-subtitle">Mode: <strong>{connector.active_mode}</strong></span>
                  </div>
                </div>
                
                {connector.healthy ? (
                  <span className="badge success" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <span style={{ display: 'inline-block', width: '6px', height: '6px', backgroundColor: 'var(--success)', borderRadius: '50%' }}></span>
                    Healthy
                  </span>
                ) : (
                  <span className="badge warning" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <span style={{ display: 'inline-block', width: '6px', height: '6px', backgroundColor: 'var(--warning)', borderRadius: '50%' }}></span>
                    Needs Setup
                  </span>
                )}
              </div>

              <div style={{ flexGrow: 1, fontSize: '0.85rem' }}>
                {connector.missing_credentials.length > 0 ? (
                  <div>
                    <p style={{ fontWeight: 600, color: 'var(--text-muted)', margin: '0 0 0.25rem' }}>Missing Credentials:</p>
                    <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
                      {connector.missing_credentials.map((cred) => (
                        <code key={cred} style={{ fontSize: '11px', padding: '1px 4px', backgroundColor: '#f1f5f9', color: '#64748b' }}>{cred}</code>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p style={{ color: 'var(--success)', fontWeight: 500, margin: 0 }}>All credentials fully configured.</p>
                )}
              </div>

              {connector.action_items.length > 0 && (
                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <strong>Next action:</strong> {connector.action_items[0]}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
