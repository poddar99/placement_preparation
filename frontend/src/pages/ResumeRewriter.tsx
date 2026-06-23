import { useState } from 'react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'

export default function ResumeRewriter() {
  const [bullet, setBullet] = useState('')
  const [context, setContext] = useState('')
  const [result, setResult] = useState<{
    original: string
    rewritten: string
    improvements: string[]
  } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const rewrite = async () => {
    if (bullet.length < 5) {
      setError('Enter at least 5 characters')
      return
    }
    setError('')
    setLoading(true)
    try {
      const { data } = await api.post('/resume/rewrite', {
        bullet_point: bullet,
        context: context || undefined,
      })
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rewrite failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Resume Rewriter"
        subtitle="Transform bullet points into professional resume lines with AI"
      />

      <Card className="mb-6 space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Bullet Point</label>
          <textarea
            value={bullet}
            onChange={(e) => setBullet(e.target.value)}
            rows={3}
            placeholder="Built Research Assistant using RAG"
            className="w-full rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Context (optional)</label>
          <input
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="AI/ML project, 3 months, team of 2"
            className="w-full rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none"
          />
        </div>
        <button
          onClick={rewrite}
          disabled={loading}
          className="rounded-lg bg-primary px-6 py-2.5 font-medium text-white hover:bg-primary-light disabled:opacity-50"
        >
          {loading ? 'Rewriting...' : 'Rewrite with AI'}
        </button>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </Card>

      {result && (
        <div className="space-y-4">
          <Card>
            <p className="text-sm text-slate-500">Original</p>
            <p className="mt-1 text-slate-600">{result.original}</p>
          </Card>
          <Card className="border-accent/30 bg-accent/5">
            <p className="text-sm font-medium text-accent">AI Rewritten</p>
            <p className="mt-2 text-lg">{result.rewritten}</p>
          </Card>
          {result.improvements.length > 0 && (
            <Card>
              <p className="mb-2 font-medium">Improvements Made</p>
              <ul className="space-y-1 text-sm text-slate-600">
                {result.improvements.map((imp, i) => (
                  <li key={i}>• {imp}</li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}