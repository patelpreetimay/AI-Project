import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import axios from 'axios'
import TrendChart from '../components/TrendChart'
import BarChart from '../components/BarChart'
import Donut from '../components/Donut'

export default function Insights(){
  const { metric } = useParams()
  const [data, setData] = useState(null)
  const [dates, setDates] = useState({
    start: new Date(Date.now() - 29*24*3600*1000).toISOString().slice(0,10),
    end: new Date().toISOString().slice(0,10)
  })

  const fetchData = () => {
    const q = new URLSearchParams(dates).toString()
    axios.get(`http://127.0.0.1:8000/api/insights/${metric}?${q}`).then(r=>setData(r.data))
  }
  useEffect(()=>{ fetchData() }, [metric, JSON.stringify(dates)])

  const download = (fmt) => {
    const base = fmt === 'csv' ? '/api/export/csv' : '/api/export/pdf'
    const url = `http://127.0.0.1:8000${base}?metric=${metric}&start=${dates.start}&end=${dates.end}`
    window.open(url, '_blank')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold capitalize">{metric} Insights</h1>
        <div className="space-x-2">
          <button onClick={()=>download('csv')} className="px-3 py-2 rounded-lg border bg-white">Export CSV</button>
          <button onClick={()=>download('pdf')} className="px-3 py-2 rounded-lg bg-black text-white">Export PDF</button>
        </div>
      </div>

      <div className="flex gap-3 items-end">
        <div>
          <label className="block text-xs text-gray-500">Start</label>
          <input type="date" value={dates.start} onChange={e=>setDates(d=>({...d, start:e.target.value}))} className="border rounded px-2 py-1"/>
        </div>
        <div>
          <label className="block text-xs text-gray-500">End</label>
          <input type="date" value={dates.end} onChange={e=>setDates(d=>({...d, end:e.target.value}))} className="border rounded px-2 py-1"/>
        </div>
        <Link to="/" className="ml-auto text-sm underline">Back to Dashboard</Link>
      </div>

      {data && <TrendChart series={data.trend} title="Trend" />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data && <BarChart items={data.hotspots} title="Hotspot Identification" />}
        {data && <Donut value={data.goal?.progress || 0} title="Goal Progress" />}
      </div>

      {data && data.anomalies?.length > 0 && (
        <div className="bg-white border rounded-xl p-4">
          <div className="font-semibold mb-2">Anomalies</div>
          <ul className="list-disc pl-5 text-sm">
            {data.anomalies.map((a,i)=>(
              <li key={i}>{a.date}: {a.value} (z={a.z.toFixed(2)})</li>
            ))}
          </ul>
        </div>
      )}

      {data && (
        <div className="bg-white border rounded-xl p-4">
          <div className="font-semibold mb-2">Estimated Cost Impact</div>
          <div className="text-2xl font-semibold">${data.cost_impact.estimated_cost}</div>
        </div>
      )}
    </div>
  )
}
