import { useRef, useState, type ChangeEvent, type DragEvent } from 'react'
import { FileText, Sparkles, Upload, X } from 'lucide-react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import type { ResumeReport } from '../types'

export default function ResumeAnalyzer() {
  const fileRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [report, setReport] = useState<ResumeReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const pickFile = (file: File | undefined) => {
    if (!file) return
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file')
      return
    }
    setError('')
    setSelectedFile(file)
    setReport(null)
  }

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    pickFile(e.target.files?.[0])
  }

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragActive(false)
    pickFile(e.dataTransfer.files?.[0])
  }

  const clearFile = () => {
    setSelectedFile(null)
    setError('')
    if (fileRef.current) fileRef.current.value = ''
  }

  const analyze = async () => {
    if (!selectedFile) {
      setError('Please select a PDF resume')
      return
    }
    setError('')
    setLoading(true)
    const form = new FormData()
    form.append('file', selectedFile)
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
        subtitle="Upload your resume PDF for AI-powered feedback via Ollama phi3"
      />

      <Card className="mb-6 overflow-hidden border-indigo-100 bg-gradient-to-br from-indigo-50/80 via-white to-violet-50/60 p-0">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={onFileChange}
          className="hidden"
        />

        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragActive(true)
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={onDrop}
          className={`border-b border-indigo-100/80 px-6 py-8 transition ${
            dragActive ? 'bg-indigo-100/50' : ''
          }`}
        >
          <div className="mx-auto flex max-w-xl flex-col items-center text-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-white shadow-lg shadow-indigo-200">
              <Upload size={28} />
            </div>
            <p className="text-lg font-semibold text-slate-800">Drop your resume here</p>
            <p className="mt-1 text-sm text-slate-500">PDF only · Max recommended size 5 MB</p>

            <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-primary to-indigo-700 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-200 transition hover:-translate-y-0.5 hover:shadow-lg"
              >
                <FileText size={18} />
                Browse PDF
              </button>
              <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                or drag & drop
              </span>
            </div>
          </div>
        </div>

        <div className="px-6 py-5">
          {selectedFile ? (
            <div className="mb-4 flex items-center justify-between gap-3 rounded-xl border border-indigo-100 bg-white px-4 py-3 shadow-sm">
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-primary">
                  <FileText size={20} />
                </div>
                <div className="min-w-0 text-left">
                  <p className="truncate font-medium text-slate-800">{selectedFile.name}</p>
                  <p className="text-xs text-slate-500">
                    {(selectedFile.size / 1024).toFixed(1)} KB · Ready to analyze
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={clearFile}
                className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                title="Remove file"
              >
                <X size={18} />
              </button>
            </div>
          ) : (
            <p className="mb-4 text-center text-sm text-slate-400">No file selected yet</p>
          )}

          <button
            onClick={analyze}
            disabled={loading || !selectedFile}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-accent to-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-violet-200 transition hover:-translate-y-0.5 hover:shadow-lg disabled:translate-y-0 disabled:opacity-50 disabled:shadow-none"
          >
            <Sparkles size={18} className={loading ? 'animate-pulse' : ''} />
            {loading ? 'Analyzing with AI...' : 'Analyze Resume'}
          </button>

          {error && <p className="mt-3 text-center text-sm text-red-600">{error}</p>}
        </div>
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