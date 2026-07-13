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
    <div>
      <div className="page-header">
        <h2>Run Telemetry</h2>
        <p>Analyze performance metrics, total token consumption, and budget logs for agent runs.</p>
      </div>

      <div className="panel">
        <div className="filters">
          <div className="filter-group">
            <label htmlFor="run-type-select">Run type</label>
            <select 
              id="run-type-select"
              value={draftRunType} 
              onChange={(event) => setDraftRunType(event.target.value)}
            >
              <option value="">All Runs</option>
              <option value="produce_content">produce_content</option>
              <option value="monthly_plan">monthly_plan</option>
              <option value="monthly_analytics">monthly_analytics</option>
              <option value="integration_smoke">integration_smoke</option>
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="from-date-input">From</label>
            <input 
              id="from-date-input"
              type="date" 
              value={draftDateFrom} 
              onChange={(event) => setDraftDateFrom(event.target.value)} 
            />
          </div>
          <div className="filter-group">
            <label htmlFor="to-date-input">To</label>
            <input 
              id="to-date-input"
              type="date" 
              value={draftDateTo} 
              onChange={(event) => setDraftDateTo(event.target.value)} 
            />
          </div>
          <button type="button" onClick={applyFilters} disabled={dateRangeInvalid}>
            Apply Filters
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '1rem' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Date presets:</span>
          <button type="button" className="secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }} onClick={() => applyPreset(7)}>Last 7 Days</button>
          <button type="button" className="secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }} onClick={() => applyPreset(30)}>Last 30 Days</button>
        </div>
      </div>

      {dateRangeInvalid && (
        <div className="toast" style={{ backgroundColor: 'var(--danger-light)', border: '1px solid #fed7d7', color: 'var(--danger)' }}>
          From date must be on or before To date.
        </div>
      )}

      {telemetry.loading && <p style={{ color: 'var(--text-muted)' }}>Loading telemetry summary...</p>}
      {telemetry.error && <p className="badge danger">{telemetry.error}</p>}

      {!telemetry.loading && !telemetry.error && telemetry.data && (
        <div>
          {telemetry.data.total_runs === 0 ? (
            <div className="panel">
              <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No telemetry runs found for selected filters.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2rem' }}>
              <div className="grid-cols-2">
                <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Executions</span>
                  <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)' }}>{telemetry.data.total_runs}</span>
                </div>
                <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Token Cost (Estimated)</span>
                  <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--success)' }}>${telemetry.data.total_estimated_cost_usd.toFixed(4)}</span>
                </div>
              </div>

              <div className="grid-cols-2">
                <div className="panel">
                  <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem' }}>Run Type Breakdown</h3>
                  <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {Object.entries(telemetry.data.by_run_type).map(([runType, count]) => (
                      <li key={runType} className="row-item" style={{ padding: '0.75rem 1rem', margin: 0 }}>
                        <span className="row-title" style={{ fontSize: '0.9rem' }}>{runType}</span>
                        <span className="badge primary">{count} runs</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="panel">
                  <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem' }}>Budget Status</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Budget-limited runs</span>
                      <span className="badge secondary">{telemetry.data.budget_limited_runs}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Budget-exceeded runs</span>
                      <span className="badge danger">{telemetry.data.budget_exceeded_runs}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="panel">
        <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem' }}>Campaign Telemetry Drilldown</h3>
        <div className="filters" style={{ margin: 0 }}>
          <div className="filter-group" style={{ flexGrow: 2 }}>
            <label htmlFor="campaign-id-drilldown">Campaign ID</label>
            <input
              id="campaign-id-drilldown"
              type="text"
              value={draftCampaignId}
              onChange={(event) => setDraftCampaignId(event.target.value)}
              placeholder="Enter active campaign ID..."
            />
          </div>
          <button type="button" onClick={loadCampaignTelemetry} disabled={!draftCampaignId}>
            Load Campaign Telemetry
          </button>
        </div>

        {campaignQuickPicks.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Quick picks:</span>
            {campaignQuickPicks.map((campaignId) => (
              <button
                key={campaignId}
                type="button"
                className="secondary"
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
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

        {campaignTelemetryError && (
          <p className="badge danger" style={{ marginTop: '1rem', display: 'inline-block' }}>{campaignTelemetryError}</p>
        )}

        {campaignTelemetrySummary && (
          <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
            <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', textTransform: 'capitalize' }}>Drilldown: {campaignTelemetrySummary.campaign_id}</h4>
            <div className="grid-cols-2" style={{ marginBottom: '1rem' }}>
              <div className="panel" style={{ padding: '1rem', margin: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Campaign Runs</span>
                <span className="row-title" style={{ fontSize: '1.2rem' }}>{campaignTelemetrySummary.total_runs}</span>
              </div>
              <div className="panel" style={{ padding: '1rem', margin: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Accumulated Cost</span>
                <span className="row-title" style={{ fontSize: '1.2rem', color: 'var(--success)' }}>${campaignTelemetrySummary.total_estimated_cost_usd.toFixed(4)}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
