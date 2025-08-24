import React from 'react'
import { Link } from 'react-router-dom'

export default function KPITile({ title, value, unit, status, metric }) {
  const color = status === 'Over Limit' ? 'text-red-600' : status === 'Watch' ? 'text-yellow-600' : 'text-green-600'
  return (
    <Link to={`/insights/${metric}`} className="block border bg-white rounded-xl p-4 shadow-sm hover:shadow">
      <div className="text-xs text-gray-500">{title}</div>
      <div className="text-2xl font-semibold mt-1">{value?.toLocaleString()} <span className="text-sm font-normal">{unit}</span></div>
      <div className={`text-xs mt-1 ${color}`}>{status}</div>
    </Link>
  )
}
