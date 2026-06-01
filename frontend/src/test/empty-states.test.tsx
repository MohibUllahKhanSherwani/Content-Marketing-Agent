import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { DashboardRoutes } from '../routes'

describe('Empty states', () => {
  it('shows empty state message for review queue when no items exist', async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.endsWith('/content-items') && (!init || init.method === 'GET')) {
        return new Response(JSON.stringify([]), { status: 200 })
      }
      if (url.endsWith('/connectors/diagnostics')) {
        return new Response(JSON.stringify({ connectors: [] }), { status: 200 })
      }
      if (url.includes('/runs/telemetry/summary')) {
        return new Response(
          JSON.stringify({
            total_runs: 0,
            successful_runs: 0,
            failed_runs: 0,
            total_estimated_cost_usd: 0,
            total_estimated_tokens: 0,
            by_run_type: {},
          }),
          { status: 200 },
        )
      }
      return new Response(JSON.stringify([]), { status: 200 })
    }) as typeof fetch

    render(
      <MemoryRouter initialEntries={['/review-queue']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    expect(await screen.findByText('No items in review queue yet.')).toBeInTheDocument()
  })

  it('shows empty state message for connector diagnostics', async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith('/connectors/diagnostics')) {
        return new Response(JSON.stringify({ connectors: [] }), { status: 200 })
      }
      if (url.includes('/runs/telemetry/summary')) {
        return new Response(
          JSON.stringify({
            total_runs: 0,
            successful_runs: 0,
            failed_runs: 0,
            total_estimated_cost_usd: 0,
            total_estimated_tokens: 0,
            by_run_type: {},
          }),
          { status: 200 },
        )
      }
      return new Response(JSON.stringify([]), { status: 200 })
    }) as typeof fetch

    render(
      <MemoryRouter initialEntries={['/connectors']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    expect(await screen.findByText('No connector diagnostics available.')).toBeInTheDocument()
  })
})
