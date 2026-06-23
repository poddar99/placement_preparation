import { useState, type FormEvent } from 'react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import type { InterviewSource } from '../types'

export default function InterviewRag() {
  const [question, setQuestion] = useState('')
  const [company, setCompany] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState<InterviewSource[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const ask = async (e?: FormEvent) => {
    e?.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post<{ answer: string; sources: InterviewSource[] }>(
        '/interview/ask',
        {
          question,
          company: company || undefined,
        }
      )
      setAnswer(data.answer)
      setSources(data.sources)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed')
    } finally {
      setLoading(false)
    }
  }

  const samples = [
    'What is usually asked in Adobe interviews?',
    'How many rounds does Google have?',
    'What DSA topics are important for Amazon?',
  ]

  return (
    <div>
      <PageHeader
        title="Interview Experience RAG"
        subtitle="Ask about real interview experiences using vector search + LLM"
      />

      <Card className="mb-6">
        <form onSubmit={ask} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Your Question</label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              rows={3}
              placeholder="What is usually asked in Microsoft interviews?"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Company Filter (optional)</label>
            <input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="Google, Amazon, Adobe..."
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-primary px-6 py-2.5 font-medium text-white hover:bg-primary-light disabled:opacity-50"
          >
            {loading ? 'Searching & generating...' : 'Ask AI'}
          </button>
        </form>

        <div className="mt-4 flex flex-wrap gap-2">
          {samples.map((s) => (
            <button
              key={s}
              onClick={() => {
                setQuestion(s)
                setTimeout(() => ask(), 0)
              }}
              className="rounded-full border border-slate-200 px-3 py-1.5 text-xs hover:bg-slate-50"
            >
              {s}
            </button>
          ))}
        </div>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </Card>

      {answer && (
        <Card className="mb-4">
          <p className="mb-2 text-sm font-medium text-accent">AI Answer</p>
          <p className="whitespace-pre-wrap text-slate-700">{answer}</p>
        </Card>
      )}

      {sources.length > 0 && (
        <div>
          <h3 className="mb-3 font-semibold">Sources</h3>
          <div className="grid gap-3 md:grid-cols-2">
            {sources.map((s, i) => (
              <Card key={i} className="text-sm">
                <p className="font-medium">{s.company} — {s.role}</p>
                <p className="text-slate-500">Outcome: {s.outcome}</p>
                {s.relevance_score != null && (
                  <p className="text-xs text-accent">
                    Relevance: {(s.relevance_score * 100).toFixed(0)}%
                  </p>
                )}
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}