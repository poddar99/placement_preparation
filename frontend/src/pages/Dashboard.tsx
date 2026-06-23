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

  const csAvg =
    data && data.cs_subjects_progress.length > 0
      ? data.cs_subjects_progress.reduce((s, x) => s + x.progress_percent, 0) /
        data.cs_subjects_progress.length
      : 0

  if (loading) return <div className="text-slate-500">Loading dashboard...</div>
  if (error) return <div className="text-red-600">{error}</div>
  if (!data) return null

  const stats = [
    { label: 'DSA Progress', value: `${data.dsa_progress_percent}%`, color: 'text-primary' },
    { label: 'CS Subjects', value: `${csAvg.toFixed(0)}%`, color: 'text-accent' },
    { label: 'Resume Score', value: data.resume_score != null ? `${data.resume_score}%` : 'N/A', color: 'text-emerald-600' },
    { label: 'Mock Interview', value: data.mock_interview_score != null ? `${data.mock_interview_score}` : 'N/A', color: 'text-amber-600' },
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
            <p className="text-4xl font-bold">{data.readiness_score}%</p>
            <p className="mt-1 text-sm text-white/80">
              {data.readiness_score >= 70
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

      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label}>
            <p className="text-sm text-slate-500">{s.label}</p>
            <p className={`mt-1 text-2xl font-bold ${s.color}`}>{s.value}</p>
          </Card>
        ))}
      </div>

      <h2 className="mb-4 text-lg font-semibold">Upcoming Companies</h2>
      {data.upcoming_companies.length === 0 ? (
        <Card>
          <p className="text-slate-500">Set target companies in your profile to see them here.</p>
        </Card>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {data.upcoming_companies.map((c) => (
            <Card key={c.id} className="flex items-start justify-between">
              <div>
                <p className="font-semibold">{c.name}</p>
                <p className="mt-1 text-sm text-slate-500 line-clamp-2">{c.description}</p>
              </div>
              <span className="rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
                {c.difficulty_level}
              </span>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}