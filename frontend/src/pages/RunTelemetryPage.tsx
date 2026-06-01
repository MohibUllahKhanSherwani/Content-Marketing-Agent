import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import {
  type TelemetrySummaryFilters,
  getCampaignTelemetrySummary,
  getRunTelemetrySummary,
} from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

const DEFAULT_FILTERS: TelemetrySummaryFilters = {}

export function RunTelemetryPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [draftRunType, setDraftRunType] = useState(searchParams.get('run_type') ?? '')
  const [draftDateFrom, setDraftDateFrom] = useState(searchParams.get('date_from') ?? '')
  const [draftDateTo, setDraftDateTo] = useState(searchParams.get('date_to') ?? '')
  const [draftCampaignId, setDraftCampaignId] = useState('')
  const [appliedFilters, setAppliedFilters] = useState<TelemetrySummaryFilters>(DEFAULT_FILTERS)
  const [campaignTelemetryError, setCampaignTelemetryError] = useState('')
  const [campaignTelemetrySummary, setCampaignTelemetrySummary] = useState<{
    campaign_id: string
    total_runs: number
    total_estimated_cost_usd: number
    by_run_type: Record<string, number>
  } | null>(null)

  const syncFiltersFromUrl = useCallback(() => {
    const runType = searchParams.get('run_type') ?? ''
    const dateFrom = searchParams.get('date_from') ?? ''
    const dateTo = searchParams.get('date_to') ?? ''
    setDraftRunType(runType)
    setDraftDateFrom(dateFrom)
    setDraftDateTo(dateTo)
    setAppliedFilters({
      runType: runType || undefined,
      dateFrom: dateFrom || undefined,
      dateTo: dateTo || undefined,
    })
  }, [searchParams])

  useEffect(() => {
    syncFiltersFromUrl()
  }, [syncFiltersFromUrl])

  const loadTelemetry = useCallback(() => getRunTelemetrySummary(appliedFilters), [appliedFilters])
  const telemetry = useAsyncData(loadTelemetry, [loadTelemetry])

  const applyFilters = () => {
    const nextFilters = {
      runType: draftRunType || undefined,
      dateFrom: draftDateFrom || undefined,
      dateTo: draftDateTo || undefined,
    }
    setAppliedFilters(nextFilters)
    const params = new URLSearchParams()
    if (nextFilters.runType) params.set('run_type', nextFilters.runType)
    if (nextFilters.dateFrom) params.set('date_from', nextFilters.dateFrom)
    if (nextFilters.dateTo) params.set('date_to', nextFilters.dateTo)
    setSearchParams(params)
  }

  const loadCampaignTelemetry = async () => {
    if (!draftCampaignId) return
    setCampaignTelemetryError('')
    try {
      const summary = await getCampaignTelemetrySummary(draftCampaignId, appliedFilters)
      setCampaignTelemetrySummary(summary)
    } catch {
      setCampaignTelemetryError('Campaign telemetry lookup failed. Check campaign id and try again.')
      setCampaignTelemetrySummary(null)
    }
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
          <p>Budget-limited runs: {telemetry.data.budget_limited_runs}</p>
          <p>Budget-exceeded runs: {telemetry.data.budget_exceeded_runs}</p>
          <ul>
            {Object.entries(telemetry.data.by_run_type).map(([runType, count]) => (
              <li key={runType}>{runType}: {count}</li>
            ))}
          </ul>
        </div>
      )}
      <hr />
      <h3>Campaign Telemetry Drilldown</h3>
      <label>
        Campaign ID
        <input
          type="text"
          value={draftCampaignId}
          onChange={(event) => setDraftCampaignId(event.target.value)}
          placeholder="Enter campaign id"
        />
      </label>
      <button type="button" onClick={loadCampaignTelemetry} disabled={!draftCampaignId}>
        Load Campaign Telemetry
      </button>
      {campaignTelemetryError && <p>{campaignTelemetryError}</p>}
      {campaignTelemetrySummary && (
        <div>
          <p>Campaign: {campaignTelemetrySummary.campaign_id}</p>
          <p>Campaign runs: {campaignTelemetrySummary.total_runs}</p>
          <p>Campaign cost: ${campaignTelemetrySummary.total_estimated_cost_usd.toFixed(4)}</p>
          <ul>
            {Object.entries(campaignTelemetrySummary.by_run_type).map(([runType, count]) => (
              <li key={runType}>{runType}: {count}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
