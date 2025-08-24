import React, { useState } from 'react'

export default function FiltersBar({ onChange }) {
  const [start, setStart] = useState(() => new Date(Date.now() - 29*24*3600*1000).toISOString().slice(0,10))
  const [end, setEnd] = useState(() => new Date().toISOString().slice(0,10))
  const [department, setDepartment] = useState('')
  return (
    <div className="bg-white border rounded-xl p-4 flex flex-wrap gap-3 items-end">
      <div>
        <label className="block text-xs text-gray-500">Start</label>
        <input type="date" value={start} onChange={e=>setStart(e.target.value)} className="border rounded px-2 py-1"/>
      </div>
      <div>
        <label className="block text-xs text-gray-500">End</label>
        <input type="date" value={end} onChange={e=>setEnd(e.target.value)} className="border rounded px-2 py-1"/>
      </div>
      <div>
        <label className="block text-xs text-gray-500">Department</label>
        <select value={department} onChange={e=>setDepartment(e.target.value)} className="border rounded px-2 py-1">
          <option value="">All</option>
          <option>Spinning</option>
          <option>Weaving</option>
          <option>Dyeing</option>
        </select>
      </div>
      <button onClick={()=>onChange({start, end, department})} className="ml-auto bg-black text-white px-3 py-2 rounded-lg">Apply</button>
    </div>
  )
}
