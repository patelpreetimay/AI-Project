import React from 'react'
import { Bar } from 'react-chartjs-2'
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default function BarChart({ items, title }) {
  const data = {
    labels: items.map(i=>i.label),
    datasets: [{ label: title, data: items.map(i=>i.value) }]
  }
  const options = { responsive: true, plugins: { legend: { display: false } } }
  return <div className="bg-white border rounded-xl p-4"><Bar data={data} options={options} /></div>
}
