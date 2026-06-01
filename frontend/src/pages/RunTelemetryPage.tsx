import { useCallback, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import {
  type TelemetrySummaryFilters,
  getCampaignTelemetrySummary,
  getRunTelemetrySummary,
} from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

const QUICK_PICKS_STORAGE_KEY = 'telemetry_campaign_quick_picks'
const MAX_QUICK_PICKS = 5

function formatDateInput(value: Date): string {
  const year = value.getUTCFullYear()
  const month = String(value.getUTCMonth() + 1).padStart(2, '0')
  const day = String(value.getUTCDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function dateWithOffsetDays(base: Date, offsetDays: number): string {
  const next = new Date(base)
  next.setUTCDate(base.getUTCDate() + offsetDays)
  return formatDateInput(next)
}

function loadCampaignQuickPicksFromStorage(): string[] {
  try {
    const raw = localStorage.getItem(QUICK_PICKS_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as unknown
    if (!Array.isArray(parsed)) return []
    const sanitized = parsed.filter((entry): entry is string => typeof entry === 'string' && entry.length > 0)
    return sanitized.slice(0, MAX_QUICK_PICKS)
  } catch {
    return []
  }
}

export function RunTelemetryPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialRunType = searchParams.get('run_type') ?? ''
  const initialDateFrom = searchParams.get('date_from') ?? ''
  const initialDateTo = searchParams.get('date_to') ?? ''
  const [draftRunType, setDraftRunType] = useState(initialRunType)
  const [draftDateFrom, setDraftDateFrom] = useState(initialDateFrom)
  const [draftDateTo, setDraftDateTo] = useState(initialDateTo)
  const [draftCampaignId, setDraftCampaignId] = useState('')
  const [appliedFilters, setAppliedFilters] = useState<TelemetrySummaryFilters>({
    runType: initialRunType || undefined,
    dateFrom: initialDateFrom || undefined,
    dateTo: initialDateTo || undefined,
  })
  const [campaignTelemetryError, setCampaignTelemetryError] = useState('')
  const [campaignTelemetrySummary, setCampaignTelemetrySummary] = useState<{
    campaign_id: string
    total_runs: number
    total_estimated_cost_usd: number
    by_run_type: Record<string, number>
  } | null>(null)
  const [campaignQuickPicks, setCampaignQuickPicks] = useState<string[]>(loadCampaignQuickPicksFromStorage)

  const saveCampaignQuickPick = (campaignId: string) => {
    const normalized = campaignId.trim()
    if (!normalized) return
    const next = [normalized, ...campaignQuickPicks.filter((item) => item !== normalized)].slice(0, MAX_QUICK_PICKS)
    setCampaignQuickPicks(next)
    localStorage.setItem(QUICK_PICKS_STORAGE_KEY, JSON.stringify(next))
  }

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

  const loadCampaignTelemetryFor = async (campaignId: string) => {
    if (!campaignId) return
    setCampaignTelemetryError('')
    try {
      const summary = await getCampaignTelemetrySummary(campaignId, appliedFilters)
      setCampaignTelemetrySummary(summary)
      saveCampaignQuickPick(campaignId)
    } catch {
      setCampaignTelemetryError('Campaign telemetry lookup failed. Check campaign id and try again.')
      setCampaignTelemetrySummary(null)
    }
  }

  const loadCampaignTelemetry = async () => loadCampaignTelemetryFor(draftCampaignId)

  const dateRangeInvalid = Boolean(draftDateFrom && draftDateTo && draftDateFrom > draftDateTo)
  const applyPreset = (days: number) => {
    const today = new Date()
    setDraftDateTo(formatDateInput(today))
    setDraftDateFrom(dateWithOffsetDays(today, -days + 1))
  }

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
      <div className="filters">
        <span>Date presets</span>
        <button type="button" onClick={() => applyPreset(7)}>Last 7 Days</button>
        <button type="button" onClick={() => applyPreset(30)}>Last 30 Days</button>
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
      {campaignQuickPicks.length > 0 && (
        <div className="filters">
          <span>Quick picks</span>
          {campaignQuickPicks.map((campaignId) => (
            <button
              key={campaignId}
              type="button"
              onClick={() => {
                setDraftCampaignId(campaignId)
                void loadCampaignTelemetryFor(campaignId)
              }}
            >
              {campaignId}
            </button>
          ))}
        </div>
      )}
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
