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
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>Content Agent Team</h1>
          <p>Multi-Channel Marketing Ops</p>
        </div>
        <nav className="nav-list" aria-label="Dashboard navigation">
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
      </aside>
      
      <div className="content-area">
        <Outlet />
      </div>
    </main>
  )
}
