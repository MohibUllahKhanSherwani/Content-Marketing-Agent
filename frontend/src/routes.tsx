import { Navigate, Route, Routes } from 'react-router-dom'

import { DashboardLayout } from './components/DashboardLayout'
import { CalendarPage } from './pages/CalendarPage'
import { CampaignWorkspacePage } from './pages/CampaignWorkspacePage'
import { ConnectorDiagnosticsPage } from './pages/ConnectorDiagnosticsPage'
import { PublicationAuditPage } from './pages/PublicationAuditPage'
import { ReviewQueuePage } from './pages/ReviewQueuePage'
import { RunTelemetryPage } from './pages/RunTelemetryPage'

export function DashboardRoutes() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="/" element={<Navigate to="/review-queue" replace />} />
        <Route path="/review-queue" element={<ReviewQueuePage />} />
        <Route path="/publication-audit" element={<PublicationAuditPage />} />
        <Route path="/campaign-workspace" element={<CampaignWorkspacePage />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/connectors" element={<ConnectorDiagnosticsPage />} />
        <Route path="/telemetry" element={<RunTelemetryPage />} />
      </Route>
    </Routes>
  )
}
