import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { ArrowLeft, MessageSquare, Plus, X } from 'lucide-react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import type { ChatMessage, MentorHistory } from '../types'

const SUGGESTIONS = [
  'I know trees and graphs. I have 2 months left. What should I study?',
  'How should I prepare for Amazon interviews?',
  'What projects should I build for placements?',
  'How to improve my resume for Google?',
]

type ViewMode = 'list' | 'chat'

function sessionPreview(session: MentorHistory): string {
  const firstUser = session.messages.find((m) => m.role === 'user')
  const text = firstUser?.content ?? session.messages[0]?.content ?? 'Empty conversation'
  return text.length > 72 ? `${text.slice(0, 72)}...` : text
}

function sessionDate(session: MentorHistory): string {
  const last = session.messages[session.messages.length - 1]
  if (!last?.created_at) return ''
  return new Date(last.created_at).toLocaleString()
}

function sortSessions(sessions: MentorHistory[]): MentorHistory[] {
  return [...sessions].sort((a, b) => {
    const aTime = a.messages[a.messages.length - 1]?.created_at ?? ''
    const bTime = b.messages[b.messages.length - 1]?.created_at ?? ''
    return bTime.localeCompare(aTime)
  })
}

export default function AiMentor() {
  const [view, setView] = useState<ViewMode>('list')
  const [sessions, setSessions] = useState<MentorHistory[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  const loadSessions = useCallback(async () => {
    setLoadingHistory(true)
    try {
      const { data } = await api.get<MentorHistory[]>('/mentor/history')
      setSessions(sortSessions(data))
    } catch {
      setSessions([])
    } finally {
      setLoadingHistory(false)
    }
  }, [])

  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  useEffect(() => {
    if (view === 'chat') {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, view, loading])

  const openChat = (history?: MentorHistory) => {
    if (history) {
      setSessionId(history.session_id)
      setMessages(history.messages)
    } else {
      setSessionId(null)
      setMessages([])
    }
    setInput('')
    setView('chat')
  }

  const exitChat = () => {
    setView('list')
    setInput('')
    loadSessions()
  }

  const send = async (text: string) => {
    if (!text.trim() || loading) return
    setInput('')
    setLoading(true)

    const userMsg: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: text,
      session_id: sessionId ?? '',
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])

    try {
      const { data } = await api.post<{ session_id: string; reply: string }>('/mentor/chat', {
        message: text,
        session_id: sessionId,
      })
      setSessionId(data.session_id)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.reply,
          session_id: data.session_id,
          created_at: new Date().toISOString(),
        },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: `Error: ${err instanceof Error ? err.message : 'Failed to get response'}`,
          session_id: sessionId ?? '',
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    send(input)
  }

  const chatTitle =
    messages.find((m) => m.role === 'user')?.content ??
    (sessionId ? 'Conversation' : 'New conversation')

  if (view === 'list') {
    return (
      <div className="flex h-[calc(100vh-4rem)] flex-col">
        <PageHeader
          title="AI Mentor"
          subtitle="Personalized placement guidance powered by Ollama phi3"
        />

        <div className="mb-4">
          <button
            onClick={() => openChat()}
            className="flex items-center gap-2 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white hover:bg-accent-light"
          >
            <Plus size={18} />
            New Chat
          </button>
        </div>

        <Card className="flex-1 overflow-y-auto">
          {loadingHistory ? (
            <p className="py-8 text-center text-slate-500">Loading conversations...</p>
          ) : sessions.length === 0 ? (
            <div className="py-10 text-center text-slate-500">
              <MessageSquare className="mx-auto mb-3 text-slate-300" size={40} />
              <p className="font-medium text-slate-700">No conversations yet</p>
              <p className="mt-1 text-sm">Start a new chat to get personalized placement advice.</p>
              <div className="mt-6 flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => {
                      openChat()
                      send(s)
                    }}
                    className="rounded-full border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
                  >
                    {s.slice(0, 50)}...
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {sessions.map((session) => (
                <button
                  key={session.session_id}
                  onClick={() => openChat(session)}
                  className="flex w-full items-start gap-3 px-2 py-4 text-left transition hover:bg-slate-50"
                >
                  <div className="mt-0.5 rounded-lg bg-primary/10 p-2 text-primary">
                    <MessageSquare size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-slate-800">
                      {sessionPreview(session)}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      {session.messages.length} messages · {sessionDate(session)}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </Card>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      <PageHeader
        title="AI Mentor"
        subtitle="Personalized placement guidance powered by Ollama phi3"
      />

      <Card className="mb-4 flex flex-1 flex-col overflow-hidden">
        <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div className="flex min-w-0 items-center gap-2">
            <button
              onClick={exitChat}
              className="flex shrink-0 items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              title="Back to conversations"
            >
              <ArrowLeft size={16} />
              Back
            </button>
            <p className="truncate text-sm font-medium text-slate-700">
              {chatTitle.length > 60 ? `${chatTitle.slice(0, 60)}...` : chatTitle}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <button
              onClick={() => openChat()}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50"
              title="Start a new conversation"
            >
              <Plus size={16} />
              New
            </button>
            <button
              onClick={exitChat}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50"
              title="Exit chat"
            >
              <X size={16} />
              Exit
            </button>
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-2 pt-4">
          {messages.length === 0 && (
            <div className="py-8 text-center text-slate-500">
              <p>Ask your AI mentor anything about placement prep.</p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="rounded-full border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
                  >
                    {s.slice(0, 50)}...
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                  msg.role === 'user'
                    ? 'bg-primary text-white'
                    : 'bg-slate-100 text-slate-800'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="text-sm text-slate-400">AI is thinking...</div>
          )}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={onSubmit} className="mt-4 flex gap-2 border-t border-slate-100 pt-4">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask your mentor..."
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 focus:border-accent focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-accent px-6 py-2.5 font-medium text-white hover:bg-accent-light disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </Card>
    </div>
  )
}