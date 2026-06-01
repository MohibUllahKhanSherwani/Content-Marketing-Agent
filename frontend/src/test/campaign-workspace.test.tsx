import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { DashboardRoutes } from '../routes'

describe('Campaign workspace page', () => {
  it('loads campaign-scoped content items when campaign id is submitted', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith('/campaigns/camp-123/content-items')) {
        return new Response(
          JSON.stringify([{ id: 'a1', title: 'Campaign Item', status: 'ready_for_review' }]),
          { status: 200 },
        )
      }
      return new Response(JSON.stringify([]), { status: 200 })
    })
    globalThis.fetch = fetchMock as typeof fetch

    render(
      <MemoryRouter initialEntries={['/campaign-workspace']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Campaign ID'), { target: { value: 'camp-123' } })
    fireEvent.click(screen.getByRole('button', { name: 'Load Campaign' }))

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/campaigns/camp-123/content-items'),
        undefined,
      )
      expect(screen.getByText(/Campaign Item/i)).toBeInTheDocument()
    })
  })
})
