import { useEffect, useState } from 'react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import type { Company, RoadmapResponse } from '../types'

export default function CompanyPrep() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [selected, setSelected] = useState<Company | null>(null)
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get<Company[]>('/companies')
      .then((res) => setCompanies(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const generateRoadmap = async (company: Company) => {
    setSelected(company)
    setGenerating(true)
    setRoadmap(null)
    try {
      const { data } = await api.post<RoadmapResponse>(`/companies/${company.id}/roadmap`, {
        weeks_available: 8,
      })
      setRoadmap(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate roadmap')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <div className="text-slate-500">Loading companies...</div>

  return (
    <div>
      <PageHeader
        title="Company Preparation"
        subtitle="AI-generated personalized roadmaps for target companies"
      />

      {error && <p className="mb-4 text-red-600">{error}</p>}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-3">
          <h2 className="font-semibold">Select Company</h2>
          {companies.map((c) => (
            <Card
              key={c.id}
              className={`cursor-pointer transition-colors hover:border-accent ${
                selected?.id === c.id ? 'border-accent ring-2 ring-accent/20' : ''
              }`}
              onClick={() => generateRoadmap(c)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">{c.name}</p>
                  <p className="mt-1 text-sm text-slate-500 line-clamp-2">{c.description}</p>
                </div>
                <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                  {c.difficulty_level}
                </span>
              </div>
            </Card>
          ))}
        </div>

        <div>
          <h2 className="mb-3 font-semibold">
            {selected ? `${selected.name} Roadmap` : 'Roadmap Preview'}
          </h2>
          {generating && (
            <Card>
              <p className="text-slate-500">Generating personalized roadmap with AI...</p>
            </Card>
          )}
          {roadmap && (
            <div className="space-y-4">
              {roadmap.content_json.overview && (
                <Card className="bg-primary/5">
                  <p>{roadmap.content_json.overview}</p>
                </Card>
              )}
              {roadmap.content_json.phases?.map((phase, i) => (
                <Card key={i}>
                  <div className="mb-2 flex items-center gap-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-accent text-sm font-bold text-white">
                      {i + 1}
                    </span>
                    <div>
                      <p className="font-semibold">{phase.title}</p>
                      <p className="text-xs text-slate-500">{phase.week_range}</p>
                    </div>
                  </div>
                  <ul className="mt-3 space-y-1 text-sm">
                    {phase.topics?.map((t, j) => (
                      <li key={j} className="text-slate-600">• {t}</li>
                    ))}
                  </ul>
                  {phase.resources && phase.resources.length > 0 && (
                    <div className="mt-3 border-t border-slate-100 pt-3">
                      <p className="text-xs font-medium text-accent">Resources</p>
                      {phase.resources.map((r, j) => (
                        <p key={j} className="text-xs text-slate-500">• {r}</p>
                      ))}
                    </div>
                  )}
                </Card>
              ))}
              {roadmap.content_json.daily_schedule && (
                <Card>
                  <p className="text-sm font-medium">Daily Schedule</p>
                  <p className="mt-1 text-sm text-slate-600">{roadmap.content_json.daily_schedule}</p>
                </Card>
              )}
            </div>
          )}
          {!generating && !roadmap && (
            <Card>
              <p className="text-slate-500">Click a company to generate an AI roadmap.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}