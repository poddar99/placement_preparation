import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import type { AnalyticsData } from '../types'

export default function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get<AnalyticsData>('/analytics')
      .then((res) => setData(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-slate-500">Loading analytics...</div>
  if (error) return <div className="text-red-600">{error}</div>
  if (!data) return null

  const chartData = data.topic_breakdown.map((t) => ({
    name: t.topic_name.length > 10 ? t.topic_name.slice(0, 10) + '…' : t.topic_name,
    progress: t.progress_percent,
  }))

  return (
    <div>
      <PageHeader title="Placement Analytics" subtitle="Track readiness and identify gaps" />

      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Readiness" value={`${data.readiness_score}%`} />
        <StatCard label="DSA Completion" value={`${data.dsa_completion_percent}%`} />
        <StatCard
          label="Resume Score"
          value={data.resume_score != null ? `${data.resume_score}%` : 'N/A'}
        />
        <StatCard
          label="Mock Interview Avg"
          value={data.mock_interview_avg != null ? data.mock_interview_avg.toFixed(1) : 'N/A'}
        />
      </div>

      {data.llm_insights && (
        <Card className="mb-6 border-accent/20 bg-accent/5">
          <p className="text-sm font-medium text-accent">AI Insights</p>
          <p className="mt-2 text-slate-700">{data.llm_insights}</p>
        </Card>
      )}

      <Card className="mb-6">
        <h3 className="mb-4 font-semibold">Topic Breakdown</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="progress" fill="#1a237e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <AreaList title="Strong Areas" items={data.strong_areas} color="emerald" />
        <AreaList title="Weak Areas" items={data.weak_areas} color="red" />
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-primary">{value}</p>
    </Card>
  )
}

function AreaList({
  title,
  items,
  color,
}: {
  title: string
  items: string[]
  color: 'emerald' | 'red'
}) {
  const bg = color === 'emerald' ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'
  return (
    <Card className={bg}>
      <h3 className="mb-3 font-semibold">{title}</h3>
      {items.length === 0 ? (
        <p className="text-sm text-slate-500">None identified yet</p>
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item} className="text-sm">
              • {item}
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}