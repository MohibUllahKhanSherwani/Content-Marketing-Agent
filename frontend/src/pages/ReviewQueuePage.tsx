import { useCallback, useMemo, useState } from 'react'

import {
  approveContentItem,
  getContentItems,
  publishDraft,
  requestChanges,
} from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

export function ReviewQueuePage() {
  const loadItems = useCallback(() => getContentItems(), [])
  const { data, loading, error, reload } = useAsyncData(loadItems, [loadItems])
  const [message, setMessage] = useState('')

  const items = useMemo(() => data ?? [], [data])
  const reviewQueue = useMemo(
    () => items.filter((item) => item.status === 'ready_for_review'),
    [items],
  )
  const displayed = reviewQueue.length > 0 ? reviewQueue : items

  const runAction = async (action: () => Promise<unknown>, successMessage: string) => {
    try {
      await action()
      setMessage(successMessage)
      reload()
    } catch {
      setMessage('Action failed. Please try again.')
    }
  }

  return (
    <section className="panel">
      <h2>Review Queue</h2>
      {message && <p>{message}</p>}
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && displayed.length === 0 && <p>No items in review queue yet.</p>}
      {!loading && !error && displayed.length > 0 && (
        <ul>
          {displayed.map((item) => (
            <li key={item.id} className="row-item">
              <span>{item.title}</span>
              <div className="row-actions">
                <button type="button" onClick={() => runAction(() => approveContentItem(item.id), 'Item approved.')}>Approve</button>
                <button type="button" onClick={() => runAction(() => requestChanges(item.id), 'Changes requested.')}>Request Changes</button>
                <button type="button" onClick={() => runAction(() => publishDraft(item.id), 'Draft published.')}>Publish Draft</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
