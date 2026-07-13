import { useCallback, useMemo, useState } from 'react'

import {
  type PublicationAuditRecord,
  getContentItems,
  getPublications,
} from '../api'
import { useAsyncData } from '../hooks/useAsyncData'

export function PublicationAuditPage() {
  const [platformFilter, setPlatformFilter] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  const loadAuditRecords = useCallback(async (): Promise<PublicationAuditRecord[]> => {
    const items = await getContentItems()
    const publicationBatches = await Promise.all(
      items.map(async (item) => {
        const publications = await getPublications(item.id)
        return publications.map((publication) => ({
          ...publication,
          content_item_id: item.id,
          content_item_title: item.title,
        }))
      }),
    )
    return publicationBatches.flat()
  }, [])

  const audit = useAsyncData(loadAuditRecords, [loadAuditRecords])
  const filtered = useMemo(() => {
    const records = audit.data ?? []
    const byPlatform = platformFilter ? records.filter((record) => record.platform === platformFilter) : records
    const query = searchTerm.trim().toLowerCase()
    if (!query) return byPlatform
    return byPlatform.filter((record) =>
      `${record.content_item_title} ${record.platform} ${record.operation}`.toLowerCase().includes(query),
    )
  }, [audit.data, platformFilter, searchTerm])

  return (
    <div>
      <div className="page-header">
        <h2>Publication Audit</h2>
        <p>Audit trail of all connector operations (drafting and publishing) executed by the agent.</p>
      </div>

      <div className="panel">
        <div className="filters">
          <div className="filter-group">
            <label htmlFor="platform-filter">Platform</label>
            <select 
              id="platform-filter"
              value={platformFilter} 
              onChange={(event) => setPlatformFilter(event.target.value)}
            >
              <option value="">All Platforms</option>
              <option value="wordpress">WordPress</option>
              <option value="hubspot">HubSpot</option>
              <option value="linkedin">LinkedIn</option>
              <option value="meta">Meta</option>
            </select>
          </div>
          <div className="filter-group" style={{ flexGrow: 2 }}>
            <label htmlFor="search-filter">Search</label>
            <input
              id="search-filter"
              type="text"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search by title, platform or operation..."
            />
          </div>
        </div>
      </div>

      <div className="panel">
        {audit.loading && <p style={{ color: 'var(--text-muted)' }}>Loading audit trail...</p>}
        {audit.error && <p className="badge danger">{audit.error}</p>}
        
        {!audit.loading && !audit.error && filtered.length === 0 && (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
            No matching publication records found.
          </p>
        )}

        {!audit.loading && !audit.error && filtered.length > 0 && (
          <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {filtered.map((record, index) => (
              <li key={`${record.content_item_id}-${record.platform}-${index}`} className="row-item">
                <div>
                  <div className="row-title">{record.content_item_title}</div>
                  <div className="row-subtitle" style={{ display: 'flex', gap: '1rem', marginTop: '0.35rem' }}>
                    <span style={{ textTransform: 'capitalize' }}><strong>Platform:</strong> {record.platform}</span>
                    <span style={{ textTransform: 'capitalize' }}><strong>Operation:</strong> {record.operation.replace('_', ' ')}</span>
                  </div>
                </div>
                
                {record.success ? (
                  <span className="badge success">Success</span>
                ) : (
                  <span className="badge danger">Failed</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
