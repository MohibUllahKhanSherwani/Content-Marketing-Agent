import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { DashboardRoutes } from '../routes'

const mockItems = [
  { id: '1', title: 'Item 1', status: 'ready_for_review' },
]

function mockFetchWithActions() {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)

    if (url.endsWith('/content-items') && (!init || init.method === 'GET')) {
      return new Response(JSON.stringify(mockItems), { status: 200 })
    }
    if (url.endsWith('/content-items/1/approve') && init?.method === 'POST') {
      return new Response(JSON.stringify({ ...mockItems[0], status: 'approved' }), { status: 200 })
    }
    if (url.endsWith('/content-items/1/request-changes') && init?.method === 'POST') {
      return new Response(JSON.stringify({ ...mockItems[0], status: 'qa_failed' }), { status: 200 })
    }
    if (url.endsWith('/content-items/1/publish-draft') && init?.method === 'POST') {
      return new Response(
        JSON.stringify({
          content_item: { ...mockItems[0], status: 'approved' },
          publication: { platform: 'wordpress', success: true, operation: 'create_draft' },
        }),
        { status: 200 },
      )
    }

    if (url.endsWith('/connectors/diagnostics')) {
      return new Response(JSON.stringify({ connectors: [] }), { status: 200 })
    }
    if (url.endsWith('/runs/telemetry/summary')) {
      return new Response(
        JSON.stringify({
          total_runs: 0,
          successful_runs: 0,
          failed_runs: 0,
          total_estimated_cost_usd: 0,
          total_estimated_tokens: 0,
          budget_limited_runs: 0,
          budget_exceeded_runs: 0,
          by_run_type: {},
        }),
        { status: 200 },
      )
    }
    return new Response(JSON.stringify([]), { status: 200 })
  })

  globalThis.fetch = fetchMock as typeof fetch
  return fetchMock
}

describe('Review queue actions', () => {
  it('submits approve action for selected item', async () => {
    const fetchMock = mockFetchWithActions()

    render(
      <MemoryRouter initialEntries={['/review-queue']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    expect(await screen.findByText('Item 1')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Approve' }))

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/content-items/1/approve'),
        expect.objectContaining({ method: 'POST' }),
      )
    })
  })
})
