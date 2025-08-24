import React from 'react'
import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
ChartJS.register(ArcElement, Tooltip, Legend)

export default function Donut({ value, title }) {
  const done = Math.max(0, Math.min(100, Math.round(value*100)))
  const data = {
    labels: ['Progress', 'Remaining'],
    datasets: [{ data: [done, 100-done] }]
  }
  const options = { cutout: '70%', plugins: { legend: { display: false } } }
  return (
    <div className="bg-white border rounded-xl p-4 flex flex-col items-center justify-center">
      <div className="text-sm mb-2">{title}</div>
      <div className="w-52"><Doughnut data={data} options={options} /></div>
      <div className="mt-2 text-xl font-semibold">{done}%</div>
    </div>
  )
}
