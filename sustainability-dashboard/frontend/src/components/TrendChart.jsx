import React from 'react'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'
ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend)

export default function TrendChart({ series, title }) {
  const data = {
    labels: series.map(p=>p.date),
    datasets: [{
      label: title,
      data: series.map(p=>p.value),
      tension: 0.3
    }]
  }
  const options = { responsive: true, plugins: { legend: { display: false } } }
  return <div className="bg-white border rounded-xl p-4"><Line data={data} options={options} /></div>
}
