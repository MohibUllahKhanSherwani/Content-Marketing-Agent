import { render, screen, waitFor } from '@testing-library/react'

import App from '../App'

const mockConnectors = {
  connectors: [
    {
      platform: 'wordpress',
      requested_mode: 'auto',
      active_mode: 'mock',
      healthy: true,
      missing_credentials: [],
      action_items: [],
    },
  ],
}

const mockItems = [
  { id: '1', title: 'Item 1', status: 'ready_for_review' },
  { id: '2', title: 'Item 2', status: 'approved' },
]

const mockTelemetry = {
  total_runs: 3,
  successful_runs: 3,
  failed_runs: 0,
  total_estimated_cost_usd: 0.02,
  total_estimated_tokens: 1300,
  budget_limited_runs: 0,
  budget_exceeded_runs: 0,
  by_run_type: { produce_content: 1, monthly_plan: 1, integration_smoke: 1 },
}

const mockPublications = [{ platform: 'wordpress', success: true, operation: 'create_draft' }]

describe('Dashboard App', () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.endsWith('/connectors/diagnostics')) {
        return new Response(JSON.stringify(mockConnectors), { status: 200 })
      }
      if (url.endsWith('/content-items') && (!init || init.method === 'GET')) {
        return new Response(JSON.stringify(mockItems), { status: 200 })
      }
      if (url.endsWith('/runs/telemetry/summary')) {
        return new Response(JSON.stringify(mockTelemetry), { status: 200 })
      }
      if (url.includes('/content-items/1/publications')) {
        return new Response(JSON.stringify(mockPublications), { status: 200 })
      }
      return new Response(JSON.stringify({}), { status: 200 })
    }) as typeof fetch
  })

  it('renders review queue route and nav links', async () => {
    render(<App />)

    expect(screen.getByRole('link', { name: 'Review Queue' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Publication Audit' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Connector Diagnostics' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Run Telemetry' })).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Review Queue' })).toBeInTheDocument()
      expect(screen.getByText('Item 1')).toBeInTheDocument()
    })
  })

  it('shows error state when an API call fails', async () => {
    globalThis.fetch = vi.fn(async () => new Response('boom', { status: 500 })) as typeof fetch

    render(<App />)

    await waitFor(() => {
      expect(screen.getAllByText('Unable to load data.').length).toBeGreaterThan(0)
    })
  })
})
