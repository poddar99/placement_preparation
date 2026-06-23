import { useRef, useState } from 'react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import type { ResumeReport } from '../types'

export default function ResumeAnalyzer() {
  const fileRef = useRef<HTMLInputElement>(null)
  const [report, setReport] = useState<ResumeReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const analyze = async () => {
    const file = fileRef.current?.files?.[0]
    if (!file) {
      setError('Please select a PDF resume')
      return
    }
    setError('')
    setLoading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      const { data } = await api.post<ResumeReport>('/resume/analyze', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setReport(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const analysis = report?.analysis_json

  return (
    <div>
      <PageHeader
        title="Resume Analyzer"
        subtitle="Upload your resume PDF for AI-powered feedback via Ollama phi2"
      />

      <Card className="mb-6">
        <input ref={fileRef} type="file" accept=".pdf" className="mb-4 block w-full text-sm" />
        <button
          onClick={analyze}
          disabled={loading}
          className="rounded-lg bg-primary px-6 py-2.5 font-medium text-white hover:bg-primary-light disabled:opacity-50"
        >
          {loading ? 'Analyzing with AI...' : 'Analyze Resume'}
        </button>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </Card>

      {report && analysis && (
        <div className="space-y-4">
          <Card className="bg-gradient-to-r from-primary/5 to-accent/5">
            <p className="text-sm text-slate-500">Resume Score</p>
            <p className="text-4xl font-bold text-primary">{report.score}%</p>
            {analysis.summary && <p className="mt-2 text-slate-600">{analysis.summary}</p>}
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            <ListCard title="Strengths" items={analysis.strengths ?? []} color="emerald" />
            <ListCard title="Weaknesses" items={analysis.weaknesses ?? []} color="red" />
            <ListCard title="Missing Skills" items={analysis.missing_skills ?? []} color="amber" />
            <ListCard title="Suggested Projects" items={analysis.suggested_projects ?? []} color="accent" />
          </div>
        </div>
      )}
    </div>
  )
}

function ListCard({
  title,
  items,
  color,
}: {
  title: string
  items: string[]
  color: string
}) {
  const colors: Record<string, string> = {
    emerald: 'border-emerald-200 bg-emerald-50',
    red: 'border-red-200 bg-red-50',
    amber: 'border-amber-200 bg-amber-50',
    accent: 'border-purple-200 bg-purple-50',
  }
  return (
    <Card className={colors[color] ?? ''}>
      <h3 className="mb-3 font-semibold">{title}</h3>
      <ul className="space-y-2">
        {items.length === 0 ? (
          <li className="text-sm text-slate-500">None identified</li>
        ) : (
          items.map((item, i) => (
            <li key={i} className="flex gap-2 text-sm">
              <span className="text-slate-400">•</span>
              {item}
            </li>
          ))
        )}
      </ul>
    </Card>
  )
}