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
    <section className="panel">
      <h2>Publication Audit</h2>
      <div className="filters">
        <label>
          Platform
          <select value={platformFilter} onChange={(event) => setPlatformFilter(event.target.value)}>
            <option value="">All</option>
            <option value="wordpress">wordpress</option>
            <option value="hubspot">hubspot</option>
            <option value="linkedin">linkedin</option>
            <option value="meta">meta</option>
          </select>
        </label>
        <label>
          Search
          <input
            type="text"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Search title or operation"
          />
        </label>
      </div>
      {audit.loading && <p>Loading...</p>}
      {audit.error && <p>{audit.error}</p>}
      {!audit.loading && !audit.error && filtered.length === 0 && <p>No publication records found.</p>}
      {!audit.loading && !audit.error && filtered.length > 0 && (
        <ul>
          {filtered.map((record, index) => (
            <li key={`${record.content_item_id}-${record.platform}-${index}`}>
              {record.content_item_title} | {record.platform} | {record.operation} | {record.success ? 'success' : 'failed'}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
