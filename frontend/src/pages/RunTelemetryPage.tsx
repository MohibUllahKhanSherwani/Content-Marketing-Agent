import { useCallback, useState } from 'react'

import { type TelemetrySummaryFilters, getRunTelemetrySummary } from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

const DEFAULT_FILTERS: TelemetrySummaryFilters = {}

export function RunTelemetryPage() {
  const [draftRunType, setDraftRunType] = useState('')
  const [draftDateFrom, setDraftDateFrom] = useState('')
  const [draftDateTo, setDraftDateTo] = useState('')
  const [appliedFilters, setAppliedFilters] = useState<TelemetrySummaryFilters>(DEFAULT_FILTERS)

  const loadTelemetry = useCallback(() => getRunTelemetrySummary(appliedFilters), [appliedFilters])
  const telemetry = useAsyncData(loadTelemetry, [loadTelemetry])

  const applyFilters = () => {
    setAppliedFilters({
      runType: draftRunType || undefined,
      dateFrom: draftDateFrom || undefined,
      dateTo: draftDateTo || undefined,
    })
  }

  const dateRangeInvalid = Boolean(draftDateFrom && draftDateTo && draftDateFrom > draftDateTo)

  return (
    <section className="panel">
      <h2>Run Telemetry</h2>
      <div className="filters">
        <label>
          Run type
          <select value={draftRunType} onChange={(event) => setDraftRunType(event.target.value)}>
            <option value="">All</option>
            <option value="produce_content">produce_content</option>
            <option value="monthly_plan">monthly_plan</option>
            <option value="monthly_analytics">monthly_analytics</option>
            <option value="integration_smoke">integration_smoke</option>
          </select>
        </label>
        <label>
          From
          <input type="date" value={draftDateFrom} onChange={(event) => setDraftDateFrom(event.target.value)} />
        </label>
        <label>
          To
          <input type="date" value={draftDateTo} onChange={(event) => setDraftDateTo(event.target.value)} />
        </label>
        <button type="button" onClick={applyFilters} disabled={dateRangeInvalid}>Apply Filters</button>
      </div>
      {dateRangeInvalid && <p>From date must be on or before To date.</p>}
      {telemetry.loading && <p>Loading...</p>}
      {telemetry.error && <p>{telemetry.error}</p>}
      {!telemetry.loading && !telemetry.error && telemetry.data && telemetry.data.total_runs === 0 && (
        <p>No telemetry runs found for selected filters.</p>
      )}
      {!telemetry.loading && !telemetry.error && telemetry.data && telemetry.data.total_runs > 0 && (
        <div>
          <p>Total runs: {telemetry.data.total_runs}</p>
          <p>Total cost: ${telemetry.data.total_estimated_cost_usd.toFixed(4)}</p>
          <ul>
            {Object.entries(telemetry.data.by_run_type).map(([runType, count]) => (
              <li key={runType}>{runType}: {count}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
