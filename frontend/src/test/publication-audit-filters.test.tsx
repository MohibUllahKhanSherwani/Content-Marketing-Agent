import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { DashboardRoutes } from '../routes'

describe('Publication audit filters', () => {
  it('filters publication records by platform and search text', async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith('/content-items')) {
        return new Response(
          JSON.stringify([
            { id: '1', title: 'Item A', status: 'approved' },
            { id: '2', title: 'Item B', status: 'approved' },
          ]),
          { status: 200 },
        )
      }
      if (url.endsWith('/content-items/1/publications')) {
        return new Response(
          JSON.stringify([{ platform: 'wordpress', operation: 'create_draft', success: true }]),
          { status: 200 },
        )
      }
      if (url.endsWith('/content-items/2/publications')) {
        return new Response(
          JSON.stringify([{ platform: 'hubspot', operation: 'create_draft', success: false }]),
          { status: 200 },
        )
      }
      return new Response(JSON.stringify([]), { status: 200 })
    }) as typeof fetch

    render(
      <MemoryRouter initialEntries={['/publication-audit']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    await screen.findByText(/Item A/i)
    fireEvent.change(screen.getByLabelText('Platform'), { target: { value: 'wordpress' } })
    fireEvent.change(screen.getByLabelText('Search'), { target: { value: 'Item A' } })

    expect(screen.getAllByText(/wordpress/i)[1]).toBeInTheDocument()
    expect(screen.queryByText(/Item B/i)).not.toBeInTheDocument()
  })
})
