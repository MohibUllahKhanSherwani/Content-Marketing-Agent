import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { DashboardRoutes } from '../routes'

describe('Dashboard routes', () => {
  it('renders review queue page', async () => {
    render(
      <MemoryRouter initialEntries={['/review-queue']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Review Queue' })).toBeInTheDocument()
  })

  it('renders connector diagnostics page', async () => {
    render(
      <MemoryRouter initialEntries={['/connectors']}>
        <DashboardRoutes />
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Connector Diagnostics' })).toBeInTheDocument()
  })
})
