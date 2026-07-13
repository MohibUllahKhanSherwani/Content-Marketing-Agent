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
  
  // Highlight items waiting for review, otherwise show all
  const reviewQueue = useMemo(
    () => items.filter((item) => item.status === 'ready_for_review' || item.status === 'idea'),
    [items],
  )
  const displayed = reviewQueue.length > 0 ? reviewQueue : items

  const runAction = async (action: () => Promise<unknown>, successMessage: string) => {
    try {
      await action()
      setMessage(successMessage)
      setTimeout(() => setMessage(''), 4000)
      reload()
    } catch {
      setMessage('Action failed. Please try again.')
      setTimeout(() => setMessage(''), 4000)
    }
  }

  const getPlatformBadge = (platform?: string) => {
    switch (platform?.toLowerCase()) {
      case 'wordpress':
        return <span className="badge primary" style={{ backgroundColor: '#e0f2fe', color: '#0369a1' }}>WordPress</span>
      case 'hubspot':
        return <span className="badge warning" style={{ backgroundColor: '#ffedd5', color: '#c2410c' }}>HubSpot</span>
      case 'linkedin':
        return <span className="badge primary" style={{ backgroundColor: '#eff6ff', color: '#1d4ed8' }}>LinkedIn</span>
      case 'meta':
        return <span className="badge primary" style={{ backgroundColor: '#fae8ff', color: '#a21caf' }}>Meta</span>
      default:
        return <span className="badge secondary">{platform || 'Unknown'}</span>
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <span className="badge success">Approved</span>
      case 'published':
        return <span className="badge success" style={{ backgroundColor: '#dcfce7', color: '#15803d' }}>Published</span>
      case 'ready_for_review':
        return <span className="badge warning">Pending Review</span>
      case 'idea':
        return <span className="badge primary">Idea</span>
      case 'publish_failed':
        return <span className="badge danger">Failed</span>
      default:
        return <span className="badge secondary">{status}</span>
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>Review & Approval Queue</h2>
        <p>Review generated content drafts, manage approval workflows, and publish to linked platforms.</p>
      </div>

      {message && (
        <div className="toast">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          {message}
        </div>
      )}

      <div className="panel">
        {loading && <p style={{ color: 'var(--text-muted)' }}>Loading items...</p>}
        {error && <p className="badge danger">{error}</p>}
        
        {!loading && !error && displayed.length === 0 && (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
            No items in the review queue yet.
          </p>
        )}

        {!loading && !error && displayed.length > 0 && (
          <ul style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {displayed.map((item) => (
              <li key={item.id} className="row-item" style={{ flexDirection: 'column', alignItems: 'stretch', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                      <span className="row-title" style={{ fontSize: '1.1rem' }}>{item.title}</span>
                      {getPlatformBadge(item.target_platform)}
                      {getStatusBadge(item.status)}
                    </div>
                    <div className="row-subtitle" style={{ marginTop: '0.5rem', display: 'flex', gap: '1rem' }}>
                      <span><strong>Format:</strong> {item.format || 'Blog Post'}</span>
                      <span><strong>ID:</strong> <code style={{ fontSize: '11px', padding: '1px 4px' }}>{item.id}</code></span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', marginTop: '0.25rem' }}>
                  <div className="row-actions">
                    {item.status !== 'approved' && item.status !== 'published' && (
                      <>
                        <button 
                          type="button" 
                          onClick={() => runAction(() => approveContentItem(item.id), 'Item approved successfully.')}
                        >
                          Approve
                        </button>
                        <button 
                          type="button" 
                          className="secondary"
                          onClick={() => runAction(() => requestChanges(item.id), 'Changes requested.')}
                        >
                          Request Changes
                        </button>
                      </>
                    )}
                    {item.status === 'approved' && (
                      <button 
                        type="button" 
                        style={{ backgroundColor: '#10b981', color: 'white' }}
                        onClick={() => runAction(() => publishDraft(item.id), 'Draft created and synced successfully.')}
                      >
                        Publish Draft
                      </button>
                    )}
                    {item.status === 'published' && (
                      <button type="button" disabled style={{ backgroundColor: '#f1f5f9', color: '#94a3b8' }}>
                        Published
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
