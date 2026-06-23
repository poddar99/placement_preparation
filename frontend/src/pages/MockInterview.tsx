import { useState } from 'react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import type { MockQuestion } from '../types'

export default function MockInterview() {
  const [focusAreas, setFocusAreas] = useState('DSA, OS, DBMS, HR')
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [questions, setQuestions] = useState<MockQuestion[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [feedback, setFeedback] = useState<{ score: number; feedback: string } | null>(null)
  const [completed, setCompleted] = useState(false)
  const [overallScore, setOverallScore] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)

  const start = async () => {
    setLoading(true)
    setCompleted(false)
    setFeedback(null)
    try {
      const { data } = await api.post<{ session_id: number; questions: MockQuestion[] }>(
        '/mock-interview/start',
        {
          focus_areas: focusAreas.split(',').map((s) => s.trim()).filter(Boolean),
          difficulty: 'medium',
          num_questions: 5,
        }
      )
      setSessionId(data.session_id)
      setQuestions(data.questions)
      setCurrentIndex(0)
      setAnswer('')
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to start')
    } finally {
      setLoading(false)
    }
  }

  const submit = async () => {
    if (!sessionId || !answer.trim()) return
    setLoading(true)
    try {
      const { data } = await api.post<{
        score: number
        feedback: string
        session_complete: boolean
        overall_score?: number
      }>(`/mock-interview/${sessionId}/answer`, {
        question_index: currentIndex,
        answer,
      })
      setFeedback({ score: data.score, feedback: data.feedback })
      setAnswer('')
      if (data.session_complete) {
        setCompleted(true)
        setOverallScore(data.overall_score ?? null)
      } else {
        setCurrentIndex((i) => i + 1)
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Submit failed')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setSessionId(null)
    setQuestions([])
    setCurrentIndex(0)
    setAnswer('')
    setFeedback(null)
    setCompleted(false)
    setOverallScore(null)
  }

  const currentQ = questions[currentIndex]

  return (
    <div>
      <PageHeader
        title="Mock Interview"
        subtitle="AI-generated questions with instant evaluation"
      />

      {!sessionId ? (
        <Card className="max-w-lg">
          <label className="mb-1 block text-sm font-medium">Focus Areas</label>
          <input
            value={focusAreas}
            onChange={(e) => setFocusAreas(e.target.value)}
            className="mb-4 w-full rounded-lg border border-slate-300 px-4 py-2.5"
          />
          <button
            onClick={start}
            disabled={loading}
            className="rounded-lg bg-primary px-6 py-2.5 font-medium text-white hover:bg-primary-light disabled:opacity-50"
          >
            {loading ? 'Starting...' : 'Start Mock Interview'}
          </button>
        </Card>
      ) : completed ? (
        <Card className="max-w-lg text-center">
          <p className="text-2xl font-bold text-primary">Interview Complete!</p>
          <p className="mt-4 text-5xl font-bold text-accent">
            {overallScore?.toFixed(1) ?? '—'} / 10
          </p>
          <button onClick={reset} className="mt-6 rounded-lg bg-primary px-6 py-2.5 text-white">
            Start New Interview
          </button>
        </Card>
      ) : (
        <div className="max-w-2xl space-y-4">
          <div className="h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full bg-primary transition-all"
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
          <p className="text-sm text-slate-500">
            Question {currentIndex + 1} of {questions.length}
          </p>

          {currentQ && (
            <Card>
              <span className="rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
                {currentQ.category}
              </span>
              <p className="mt-4 text-lg font-medium">{currentQ.question}</p>
            </Card>
          )}

          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={5}
            placeholder="Type your answer..."
            className="w-full rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none"
          />

          <button
            onClick={submit}
            disabled={loading || !answer.trim()}
            className="rounded-lg bg-accent px-6 py-2.5 font-medium text-white hover:bg-accent-light disabled:opacity-50"
          >
            {loading ? 'Evaluating...' : 'Submit Answer'}
          </button>

          {feedback && (
            <Card className="border-emerald-200 bg-emerald-50">
              <p className="font-medium text-emerald-700">Score: {feedback.score}/10</p>
              <p className="mt-2 text-sm text-slate-700">{feedback.feedback}</p>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}