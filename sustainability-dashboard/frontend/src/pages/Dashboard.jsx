import React, { useEffect, useState } from 'react'
import axios from 'axios'
import KPITile from '../components/KpiTile'
import AlertsPanel from '../components/AlertsPanel'
import FiltersBar from '../components/FiltersBar'

export default function Dashboard() {
  const [params, setParams] = useState({})
  const [kpis, setKpis] = useState(null)

  const fetchKpis = () => {
    const q = new URLSearchParams(params).toString()
    axios.get(`http://127.0.0.1:8000/api/kpis?${q}`).then(r => setKpis(r.data))
  }

  useEffect(() => { fetchKpis(); const id = setInterval(fetchKpis, 30000); return ()=>clearInterval(id) }, [JSON.stringify(params)])

  return (
    <div className="space-y-6">
      <FiltersBar onChange={setParams} />
      <div className="flex flex-col md:flex-row gap-6">
        <div className="flex-1">
          <h2 className="text-2xl font-bold mb-4">Key Performance Indicators</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {kpis && <KPITile title="Energy" metric="energy" value={kpis.kpis.energy.value} unit={kpis.kpis.energy.unit} status={kpis.kpis.energy.status} />}
            {kpis && <KPITile title="Water" metric="water" value={kpis.kpis.water.value} unit={kpis.kpis.water.unit} status={kpis.kpis.water.status} />}
            {kpis && <KPITile title="Waste" metric="waste" value={kpis.kpis.waste.value} unit={kpis.kpis.waste.unit} status={kpis.kpis.waste.status} />}
            {kpis && <KPITile title="Emissions" metric="emissions" value={kpis.kpis.emissions.value} unit={kpis.kpis.emissions.unit} status={kpis.kpis.emissions.status} />}
            {kpis && <KPITile title="Overall Performance" metric="overall" value={kpis.overall.score} unit="%" status={kpis.overall.status} />}
          </div>
        </div>
        <AlertsPanel />
      </div>
    </div>
  )
}
