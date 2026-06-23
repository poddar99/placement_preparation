import { useEffect, useState } from 'react'
import { ExternalLink, RefreshCw } from 'lucide-react'
import { api } from '../api/client'
import Card from '../components/Card'
import PageHeader from '../components/PageHeader'
import { useAuth } from '../context/AuthContext'
import type { DsaFullProgress, LeetCodeStats } from '../types'

const DEFAULT_LC_USER = 'soumyapoddar16'

export default function DsaTracker() {
  const { user, updateProfile } = useAuth()
  const [progress, setProgress] = useState<DsaFullProgress | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState('')
  const [lcUsername, setLcUsername] = useState(user?.leetcode_username || DEFAULT_LC_USER)

  const load = () => {
    setLoading(true)
    api
      .get<DsaFullProgress>('/dsa/progress')
      .then((res) => setProgress(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    if (!loading && progress && !progress.leetcode?.last_synced && lcUsername.trim()) {
      syncLeetCode()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, progress?.leetcode?.last_synced])

  useEffect(() => {
    if (user?.leetcode_username) {
      setLcUsername(user.leetcode_username)
    }
  }, [user?.leetcode_username])

  const syncLeetCode = async () => {
    setSyncing(true)
    setError('')
    try {
      if (lcUsername && lcUsername !== user?.leetcode_username) {
        await updateProfile({ leetcode_username: lcUsername } as Parameters<typeof updateProfile>[0])
      }
      const { data } = await api.post<DsaFullProgress>('/dsa/leetcode/sync', {
        username: lcUsername || undefined,
      })
      setProgress(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'LeetCode sync failed')
    } finally {
      setSyncing(false)
    }
  }

  if (loading) return <div className="text-slate-500">Loading DSA progress...</div>
  if (error && !progress) return <div className="text-red-600">{error}</div>
  if (!progress) return null

  const lc = progress.leetcode

  return (
    <div>
      <PageHeader
        title="DSA Tracker"
        subtitle="Auto-synced with your LeetCode profile"
      />

      <Card className="border-orange-200 bg-gradient-to-r from-orange-50 to-amber-50">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-orange-700">LeetCode Sync</span>
              {lc?.profile_url && (
                <a
                  href={lc.profile_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-sm text-orange-600 hover:underline"
                >
                  @{lc.username} <ExternalLink size={14} />
                </a>
              )}
            </div>
            <p className="mt-1 text-sm text-slate-600">
              Fetches solved problems, contest rating & topic tags from LeetCode GraphQL API
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <input
              value={lcUsername}
              onChange={(e) => setLcUsername(e.target.value)}
              placeholder="LeetCode username"
              className="rounded-lg border border-orange-200 bg-white px-3 py-2 text-sm"
            />
            <button
              onClick={syncLeetCode}
              disabled={syncing || !lcUsername.trim()}
              className="flex items-center gap-2 rounded-lg bg-orange-600 px-4 py-2 text-sm font-medium text-white hover:bg-orange-700 disabled:opacity-50"
            >
              <RefreshCw size={16} className={syncing ? 'animate-spin' : ''} />
              {syncing ? 'Syncing...' : 'Sync LeetCode'}
            </button>
          </div>
        </div>

        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

        {lc ? (
          <>
            <LeetCodeStatsPanel stats={lc} />
            <LeetCodeTagsPanel tagCounts={lc.tag_counts} />
          </>
        ) : (
          <p className="mt-4 text-sm text-slate-500">
            Enter your LeetCode username and sync to load your stats.
          </p>
        )}
      </Card>
    </div>
  )
}

function LeetCodeStatsPanel({ stats }: { stats: LeetCodeStats }) {
  return (
    <div className="mt-4 grid grid-cols-2 gap-3 border-t border-orange-200 pt-4 md:grid-cols-4 lg:grid-cols-7">
      <LcStat label="Total" value={stats.total_solved} />
      <LcStat label="Easy" value={stats.easy_solved} color="text-emerald-600" />
      <LcStat label="Medium" value={stats.medium_solved} color="text-amber-600" />
      <LcStat label="Hard" value={stats.hard_solved} color="text-red-600" />
      <LcStat label="Rating" value={stats.contest_rating} color="text-primary" />
      <LcStat label="Contests" value={stats.contest_attended} />
      <LcStat label="Ranking" value={stats.ranking ? `#${stats.ranking.toLocaleString()}` : 'N/A'} />
      {stats.last_synced && (
        <div className="col-span-2 rounded-lg bg-white/70 px-3 py-2 text-center md:col-span-4 lg:col-span-8">
          <p className="text-xs text-slate-500">Last synced</p>
          <p className="text-sm font-medium text-slate-700">
            {new Date(stats.last_synced).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  )
}

function LeetCodeTagsPanel({ tagCounts }: { tagCounts: Record<string, number> }) {
  const tags = Object.entries(tagCounts)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)

  if (tags.length === 0) return null

  const maxCount = tags[0][1]

  return (
    <div className="mt-4 border-t border-orange-200 pt-4">
      <p className="mb-3 text-sm font-semibold text-orange-800">Top LeetCode Tags</p>
      <div className="space-y-2">
        {tags.map(([tag, count]) => (
          <div key={tag}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-slate-700">{tag}</span>
              <span className="font-medium text-slate-600">{count}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/80">
              <div
                className="h-full rounded-full bg-orange-500 transition-all"
                style={{ width: `${(count / maxCount) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function LcStat({
  label,
  value,
  color = 'text-slate-800',
}: {
  label: string
  value: string | number
  color?: string
}) {
  return (
    <div className="rounded-lg bg-white/70 px-3 py-2 text-center">
      <p className="text-xs text-slate-500">{label}</p>
      <p className={`text-lg font-bold ${color}`}>{value}</p>
    </div>
  )
}