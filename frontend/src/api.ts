export type ConnectorDiagnostic = {
  platform: string
  requested_mode: string
  active_mode: string
  healthy: boolean
  missing_credentials: string[]
  action_items: string[]
}

export type ContentItem = {
  id: string
  title: string
  status: string
  scheduled_at?: string | null
  target_platform?: string
  format?: string
  body?: string
}

export type Publication = {
  platform: string
  success: boolean
  operation: string
}

export type PublicationAuditRecord = Publication & {
  content_item_id: string
  content_item_title: string
}

export type TelemetrySummary = {
  total_runs: number
  successful_runs: number
  failed_runs: number
  total_estimated_cost_usd: number
  total_estimated_tokens: number
  budget_limited_runs: number
  budget_exceeded_runs: number
  by_run_type: Record<string, number>
}

export type TelemetrySummaryFilters = {
  runType?: string
  dateFrom?: string
  dateTo?: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`)
  }
  return (await response.json()) as T
}

export async function getConnectorDiagnostics(): Promise<ConnectorDiagnostic[]> {
  const payload = await requestJson<{ connectors: ConnectorDiagnostic[] }>('/connectors/diagnostics')
  return payload.connectors
}

export async function getContentItems(): Promise<ContentItem[]> {
  return requestJson<ContentItem[]>('/content-items')
}

export async function getCalendarItems(): Promise<ContentItem[]> {
  return requestJson<ContentItem[]>('/calendar')
}

export async function getCampaignContentItems(campaignId: string): Promise<ContentItem[]> {
  return requestJson<ContentItem[]>(`/campaigns/${campaignId}/content-items`)
}

export async function getPublications(contentItemId: string): Promise<Publication[]> {
  return requestJson<Publication[]>(`/content-items/${contentItemId}/publications`)
}

function buildTelemetrySummaryQuery(filters: TelemetrySummaryFilters): string {
  const params = new URLSearchParams()
  if (filters.runType) params.set('run_type', filters.runType)
  if (filters.dateFrom) params.set('date_from', `${filters.dateFrom}T00:00:00Z`)
  if (filters.dateTo) params.set('date_to', `${filters.dateTo}T23:59:59Z`)
  const query = params.toString()
  return query.length > 0 ? `?${query}` : ''
}

export async function getRunTelemetrySummary(filters: TelemetrySummaryFilters = {}): Promise<TelemetrySummary> {
  return requestJson<TelemetrySummary>(`/runs/telemetry/summary${buildTelemetrySummaryQuery(filters)}`)
}

export async function getCampaignTelemetrySummary(
  campaignId: string,
  filters: TelemetrySummaryFilters = {},
): Promise<TelemetrySummary & { campaign_id: string }> {
  return requestJson<TelemetrySummary & { campaign_id: string }>(
    `/campaigns/${campaignId}/telemetry-summary${buildTelemetrySummaryQuery(filters)}`,
  )
}

export async function approveContentItem(contentItemId: string): Promise<ContentItem> {
  return requestJson<ContentItem>(`/content-items/${contentItemId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approver: 'dashboard_operator' }),
  })
}

export async function requestChanges(contentItemId: string): Promise<ContentItem> {
  return requestJson<ContentItem>(`/content-items/${contentItemId}/request-changes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approver: 'dashboard_operator', notes: 'Needs revision before approval.' }),
  })
}

export async function publishDraft(contentItemId: string): Promise<{ content_item: ContentItem; publication: Publication }> {
  return requestJson<{ content_item: ContentItem; publication: Publication }>(`/content-items/${contentItemId}/publish-draft`, {
    method: 'POST',
  })
}
