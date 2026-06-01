import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { DashboardRoutes } from '../routes'

describe('Telemetry filters', () => {
  it('applies run type and date filters to telemetry summary request', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/runs/telemetry/summary')) {
        return new Response(
          JSON.stringify({
            total_runs: 1,
            successful_runs: 1,
            failed_runs: 0,
            total_estimated_cost_usd: 0.01,
            total_estimated_tokens: 200,
            budget_limited_runs: 0,
            budget_exceeded_runs: 0,
            by_run_type: { produce_content: 1 },
          }),
          { status: 200 },
        )
      }
      return new Response(JSON.stringify({ connectors: [] }), { status: 200 })
    })
    globalThis.fetch = fetchMock as typeof fetch

    render(
      <MemoryRouter initialEntries={['/telemetry']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    await screen.findByRole('heading', { name: 'Run Telemetry' })

    fireEvent.change(screen.getByLabelText('Run type'), { target: { value: 'produce_content' } })
    fireEvent.change(screen.getByLabelText('From'), { target: { value: '2026-06-01' } })
    fireEvent.change(screen.getByLabelText('To'), { target: { value: '2026-06-30' } })
    fireEvent.click(screen.getByRole('button', { name: 'Apply Filters' }))

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/runs/telemetry/summary?run_type=produce_content&date_from=2026-06-01T00%3A00%3A00Z&date_to=2026-06-30T23%3A59%3A59Z'),
        undefined,
      )
    })
  })

  it('hydrates telemetry filters from URL query params and calls summary with those filters', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/runs/telemetry/summary')) {
        return new Response(
          JSON.stringify({
            total_runs: 1,
            successful_runs: 1,
            failed_runs: 0,
            total_estimated_cost_usd: 0.01,
            total_estimated_tokens: 200,
            budget_limited_runs: 0,
            budget_exceeded_runs: 0,
            by_run_type: { monthly_plan: 1 },
          }),
          { status: 200 },
        )
      }
      return new Response(JSON.stringify({ connectors: [] }), { status: 200 })
    })
    globalThis.fetch = fetchMock as typeof fetch

    render(
      <MemoryRouter initialEntries={['/telemetry?run_type=monthly_plan&date_from=2026-06-01&date_to=2026-06-30']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    await screen.findByRole('heading', { name: 'Run Telemetry' })
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/runs/telemetry/summary?run_type=monthly_plan&date_from=2026-06-01T00%3A00%3A00Z&date_to=2026-06-30T23%3A59%3A59Z'),
        undefined,
      )
    })
    expect(screen.getByLabelText('Run type')).toHaveValue('monthly_plan')
    expect(screen.getByLabelText('From')).toHaveValue('2026-06-01')
    expect(screen.getByLabelText('To')).toHaveValue('2026-06-30')
  })
})
