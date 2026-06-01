import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { DashboardRoutes } from '../routes'

describe('Calendar page', () => {
  it('renders scheduled calendar items', async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith('/calendar')) {
        return new Response(
          JSON.stringify([
            {
              id: 'cal-1',
              title: 'Scheduled Blog',
              status: 'briefed',
              scheduled_at: '2026-06-22T10:00:00Z',
            },
          ]),
          { status: 200 },
        )
      }
      return new Response(JSON.stringify([]), { status: 200 })
    }) as typeof fetch

    render(
      <MemoryRouter initialEntries={['/calendar']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Content Calendar' })).toBeInTheDocument()
    expect(await screen.findByText(/Scheduled Blog/i)).toBeInTheDocument()
  })
})
