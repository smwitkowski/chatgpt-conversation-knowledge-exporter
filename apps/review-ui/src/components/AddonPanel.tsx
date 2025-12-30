import { useEffect, useState } from 'react'

interface Addon {
  addon_id: string
  name: string
  description: string
  capabilities: string[]
}

interface AddonPanelProps {
  targetKind: 'topic' | 'conversation'
  targetId: string | number
}

export default function AddonPanel({ targetKind, targetId }: AddonPanelProps) {
  const [addons, setAddons] = useState<Addon[]>([])
  const [selectedAddon, setSelectedAddon] = useState<string | null>(null)
  const [panelData, setPanelData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/addons')
      .then(res => res.json())
      .then(data => {
        // Filter to panel addons only
        const panelAddons = (data.addons || []).filter((a: Addon) => a.capabilities.includes('panel'))
        setAddons(panelAddons)
        if (panelAddons.length > 0) {
          setSelectedAddon(panelAddons[0].addon_id)
        }
      })
      .catch(err => console.error('Failed to load addons:', err))
  }, [])

  useEffect(() => {
    if (selectedAddon) {
      loadPanelData()
    }
  }, [selectedAddon, targetKind, targetId])

  const loadPanelData = async () => {
    if (!selectedAddon) return
    setLoading(true)
    try {
      const response = await fetch(`/api/addons/${selectedAddon}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kind: targetKind, id: targetId }),
      })
      const data = await response.json()
      setPanelData(data.data)
    } catch (err) {
      console.error('Failed to load panel data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (addons.length === 0) {
    return null
  }

  return (
    <div className="card">
      <h2>Add-ons</h2>
      <div style={{ marginBottom: '15px' }}>
        <select
          value={selectedAddon || ''}
          onChange={(e) => setSelectedAddon(e.target.value)}
          style={{ padding: '8px', border: '1px solid #ddd', borderRadius: '4px', width: '100%' }}
        >
          {addons.map(addon => (
            <option key={addon.addon_id} value={addon.addon_id}>
              {addon.name}
            </option>
          ))}
        </select>
      </div>
      {loading && <p>Loading...</p>}
      {panelData && !loading && (
        <div>
          {selectedAddon === 'topic-stats' && (
            <div>
              <h3>Statistics</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
                <div>
                  <strong>Conversations:</strong> {panelData.conversation_count || 0}
                </div>
                {panelData.atom_type_distribution && (
                  <div>
                    <strong>Atom Types:</strong>
                    <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                      {Object.entries(panelData.atom_type_distribution).map(([type, count]) => (
                        <li key={type}>{type}: {count}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {panelData.status_distribution && (
                  <div>
                    <strong>Status:</strong>
                    <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                      {Object.entries(panelData.status_distribution).map(([status, count]) => (
                        <li key={status}>{status}: {count}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {panelData.atom_topic_distribution && (
                  <div>
                    <strong>Top Atom Topics:</strong>
                    <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                      {Object.entries(panelData.atom_topic_distribution).map(([topic, count]) => (
                        <li key={topic}>{topic}: {count}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
          {selectedAddon !== 'topic-stats' && (
            <pre style={{ background: '#f9f9f9', padding: '15px', borderRadius: '4px', overflow: 'auto' }}>
              {JSON.stringify(panelData, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
