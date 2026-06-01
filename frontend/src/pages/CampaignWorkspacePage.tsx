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

  return (
    <section className="panel">
      <h2>Campaign Workspace</h2>
      <div className="filters">
        <label>
          Campaign ID
          <input
            type="text"
            value={draftCampaignId}
            onChange={(event) => setDraftCampaignId(event.target.value)}
            placeholder="Enter campaign id"
          />
        </label>
        <button type="button" onClick={() => setCampaignId(draftCampaignId.trim())}>Load Campaign</button>
      </div>
      {campaignItems.loading && campaignId && <p>Loading...</p>}
      {campaignItems.error && <p>{campaignItems.error}</p>}
      {!campaignItems.loading && !campaignItems.error && campaignId && (campaignItems.data ?? []).length === 0 && (
        <p>No content items found for this campaign.</p>
      )}
      {!campaignItems.loading && !campaignItems.error && (campaignItems.data ?? []).length > 0 && (
        <ul>
          {(campaignItems.data ?? []).map((item) => (
            <li key={item.id}>{item.title} | {item.status}</li>
          ))}
        </ul>
      )}
    </section>
  )
}
