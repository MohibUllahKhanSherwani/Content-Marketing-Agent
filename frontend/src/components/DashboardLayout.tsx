import { NavLink, Outlet } from 'react-router-dom'

const links = [
  { to: '/review-queue', label: 'Review Queue' },
  { to: '/publication-audit', label: 'Publication Audit' },
  { to: '/campaign-workspace', label: 'Campaign Workspace' },
  { to: '/calendar', label: 'Content Calendar' },
  { to: '/connectors', label: 'Connector Diagnostics' },
  { to: '/telemetry', label: 'Run Telemetry' },
]

export function DashboardLayout() {
  return (
    <main className="dashboard">
      <header className="hero">
        <h1>Content Operations Dashboard</h1>
        <p>Operate safe approval, publication, and telemetry flows.</p>
        <nav className="nav-grid" aria-label="Dashboard navigation">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <Outlet />
    </main>
  )
}
