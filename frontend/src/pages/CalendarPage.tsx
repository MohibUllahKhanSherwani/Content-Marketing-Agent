import { useCallback } from 'react'

import { getCalendarItems } from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

export function CalendarPage() {
  const calendar = useAsyncData(useCallback(() => getCalendarItems(), []), [])

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved': return <span className="badge success">Approved</span>
      case 'published': return <span className="badge success" style={{ backgroundColor: '#dcfce7', color: '#15803d' }}>Published</span>
      case 'ready_for_review': return <span className="badge warning">Pending Review</span>
      case 'idea': return <span className="badge primary">Idea</span>
      default: return <span className="badge secondary">{status}</span>
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>Content Calendar</h2>
        <p>View and manage scheduled publication timelines for all content assets.</p>
      </div>

      <div className="panel">
        {calendar.loading && <p style={{ color: 'var(--text-muted)' }}>Loading scheduled items...</p>}
        {calendar.error && <p className="badge danger">{calendar.error}</p>}
        
        {!calendar.loading && !calendar.error && (calendar.data ?? []).length === 0 && (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
            No scheduled content items yet.
          </p>
        )}

        {!calendar.loading && !calendar.error && (calendar.data ?? []).length > 0 && (
          <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {(calendar.data ?? []).map((item) => (
              <li key={item.id} className="row-item">
                <div>
                  <span className="row-title">{item.title}</span>
                  <div className="row-subtitle" style={{ marginTop: '0.25rem' }}>
                    Scheduled: <strong>{item.scheduled_at || 'Unscheduled'}</strong>
                  </div>
                </div>
                {getStatusBadge(item.status)}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
