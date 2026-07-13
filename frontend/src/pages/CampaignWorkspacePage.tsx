import { useCallback, useState } from 'react'

import { getCampaignContentItems } from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

export function CampaignWorkspacePage() {
  const [draftCampaignId, setDraftCampaignId] = useState('')
  const [campaignId, setCampaignId] = useState('')

  const campaignItems = useAsyncData(
    useCallback(
      () => (campaignId ? getCampaignContentItems(campaignId) : Promise.resolve([])),
      [campaignId],
    ),
    [campaignId],
  )

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
        <h2>Campaign Workspace</h2>
        <p>Analyze and manage campaign briefs, content pipelines, and distribution schedules.</p>
      </div>

      <div className="panel">
        <div className="filters" style={{ margin: 0 }}>
          <div className="filter-group" style={{ flexGrow: 2 }}>
            <label htmlFor="campaign-id-input">Campaign ID</label>
            <input
              id="campaign-id-input"
              type="text"
              value={draftCampaignId}
              onChange={(event) => setDraftCampaignId(event.target.value)}
              placeholder="Enter active campaign ID (e.g. campaign_001)..."
            />
          </div>
          <button type="button" onClick={() => setCampaignId(draftCampaignId.trim())}>
            Load Campaign Content
          </button>
        </div>
      </div>

      {campaignId && (
        <div className="panel">
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem' }}>Content Items for Campaign</h3>
          
          {campaignItems.loading && <p style={{ color: 'var(--text-muted)' }}>Loading campaign content...</p>}
          {campaignItems.error && <p className="badge danger">{campaignItems.error}</p>}
          
          {!campaignItems.loading && !campaignItems.error && (campaignItems.data ?? []).length === 0 && (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1rem 0' }}>
              No content items found for this campaign.
            </p>
          )}

          {!campaignItems.loading && !campaignItems.error && (campaignItems.data ?? []).length > 0 && (
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {(campaignItems.data ?? []).map((item) => (
                <li key={item.id} className="row-item">
                  <span className="row-title">{item.title}</span>
                  {getStatusBadge(item.status)}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
