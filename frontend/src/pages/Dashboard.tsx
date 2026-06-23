import { useEffect, useState } from 'react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import { useAuth } from '../context/AuthContext'
import type { DashboardData } from '../types'

export default function Dashboard() {
  const { user } = useAuth()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get<DashboardData>('/dashboard')
      .then((res) => setData(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-slate-500">Loading dashboard...</div>
  if (error) return <div className="text-red-600">{error}</div>
  if (!data) return null

  const readiness = Math.round(data.readiness_score)
  const dsaPercent = Math.min(100, Math.round(data.dsa_progress_percent))

  const stats = [
    { label: 'DSA Progress', value: `${dsaPercent}%`, color: 'text-primary' },
    {
      label: 'Resume Score',
      value: data.resume_score != null ? `${Math.round(data.resume_score)}%` : 'N/A',
      color: 'text-emerald-600',
    },
    {
      label: 'Mock Interview',
      value: `${Math.round(data.mock_interview_score ?? 0)}%`,
      color: 'text-amber-600',
    },
  ]

  return (
    <div>
      <PageHeader
        title={`Welcome, ${user?.full_name?.split(' ')[0] ?? 'Student'}`}
        subtitle="Your placement preparation at a glance"
      />

      <Card className="mb-6 bg-gradient-to-r from-primary to-accent text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-white/70">Placement Readiness</p>
            <p className="text-4xl font-bold">{readiness}%</p>
            <p className="mt-1 text-sm text-white/80">
              {readiness >= 70
                ? "You're on track — keep going!"
                : 'Focus on weak areas to improve.'}
            </p>
          </div>
          <div className="text-right text-sm text-white/80">
            <p>{data.total_problems_solved} problems solved</p>
            <p>Rating: {data.contest_rating}</p>
          </div>
        </div>
      </Card>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {stats.map((s) => (
          <Card key={s.label}>
            <p className="text-sm text-slate-500">{s.label}</p>
            <p className={`mt-1 text-2xl font-bold ${s.color}`}>{s.value}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}