import React, { useEffect, useState } from 'react'
import axios from 'axios'

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState([])
  useEffect(() => { axios.get('http://127.0.0.1:8000/api/alerts').then(r => setAlerts(r.data)) }, [])
  return (
    <aside className="w-full md:w-80">
      <div className="bg-white border rounded-xl p-4">
        <div className="font-semibold mb-3">Critical Alerts</div>
        <div className="space-y-3">
          {alerts.map(a => (
            <div key={a.id} className="flex items-start justify-between border-t pt-3 first:border-0 first:pt-0">
              <div>
                <div className="text-sm font-medium">{a.title}</div>
                <div className="text-xs text-gray-500">{a.message}</div>
              </div>
              <div className="text-xs text-gray-700">{a.date}</div>
            </div>
          ))}
          {alerts.length === 0 && <div className="text-xs text-green-600">All good ✔</div>}
        </div>
      </div>
    </aside>
  )
}
