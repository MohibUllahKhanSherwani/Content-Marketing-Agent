import { useCallback } from 'react'

import { getConnectorDiagnostics } from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

export function ConnectorDiagnosticsPage() {
  const diagnostics = useAsyncData(useCallback(() => getConnectorDiagnostics(), []), [])

  return (
    <section className="panel">
      <h2>Connector Diagnostics</h2>
      {diagnostics.loading && <p>Loading...</p>}
      {diagnostics.error && <p>{diagnostics.error}</p>}
      {!diagnostics.loading && !diagnostics.error && (diagnostics.data ?? []).length === 0 && (
        <p>No connector diagnostics available.</p>
      )}
      {!diagnostics.loading && !diagnostics.error && (diagnostics.data ?? []).length > 0 && (
        <ul>
          {(diagnostics.data ?? []).map((connector) => (
            <li key={connector.platform}>
              {connector.platform} | {connector.active_mode} | {connector.healthy ? 'healthy' : 'attention'}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
