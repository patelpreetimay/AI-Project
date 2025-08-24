import React from 'react'
import { Outlet, Link } from 'react-router-dom'

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-xl font-bold">Dashboard</div>
          <nav className="text-sm space-x-4">
            <Link to="/" className="hover:underline">home</Link>
            <a href="http://127.0.0.1:8000/docs" className="hover:underline">api</a>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-6">
        <Outlet />
      </main>
      <footer className="text-center text-xs text-gray-500 py-8">
        © 2025 Sustainability Inc. · Privacy Policy · Terms of Service
      </footer>
    </div>
  )
}
