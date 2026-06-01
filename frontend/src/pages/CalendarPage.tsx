import { useCallback } from 'react'

import { getCalendarItems } from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

export function CalendarPage() {
  const calendar = useAsyncData(useCallback(() => getCalendarItems(), []), [])

  return (
    <section className="panel">
      <h2>Content Calendar</h2>
      {calendar.loading && <p>Loading...</p>}
      {calendar.error && <p>{calendar.error}</p>}
      {!calendar.loading && !calendar.error && (calendar.data ?? []).length === 0 && (
        <p>No scheduled content items yet.</p>
      )}
      {!calendar.loading && !calendar.error && (calendar.data ?? []).length > 0 && (
        <ul>
          {(calendar.data ?? []).map((item) => (
            <li key={item.id}>
              {item.title} | {item.status} | {item.scheduled_at ?? 'unscheduled'}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
