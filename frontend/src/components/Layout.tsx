import { NavLink, Outlet } from 'react-router-dom'
import {
  BarChart3,
  Bot,
  Building2,
  Code2,
  FileText,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Mic,
  PenLine,
  Rocket,
  User,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const navSections = [
  {
    title: 'Overview',
    items: [
      { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    ],
  },
  {
    title: 'Practice',
    items: [
      { to: '/dsa', icon: Code2, label: 'DSA Tracker' },
      { to: '/resume', icon: FileText, label: 'Resume Analyzer' },
      { to: '/resume-rewrite', icon: PenLine, label: 'Resume Rewriter' },
      { to: '/mentor', icon: Bot, label: 'AI Mentor' },
    ],
  },
  {
    title: 'Interview',
    items: [
      { to: '/companies', icon: Building2, label: 'Company Prep' },
      { to: '/interview', icon: MessageSquare, label: 'Interview RAG' },
      { to: '/mock-interview', icon: Mic, label: 'Mock Interview' },
    ],
  },
  {
    title: 'Account',
    items: [{ to: '/profile', icon: User, label: 'Profile' }],
  },
]

function userInitials(name?: string | null): string {
  if (!name) return 'U'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
}

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-white/5 bg-[#12141c] text-slate-200 shadow-2xl">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -left-10 top-0 h-40 w-40 rounded-full bg-violet-600/20 blur-3xl" />
          <div className="absolute bottom-20 -right-8 h-32 w-32 rounded-full bg-cyan-500/10 blur-3xl" />
        </div>

        <div className="relative border-b border-white/8 px-5 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-cyan-500 text-white shadow-lg shadow-violet-900/40">
              <Rocket size={20} />
            </div>
            <div>
              <h1 className="text-base font-bold tracking-tight text-white">PlacementPilot</h1>
              <p className="text-[11px] font-medium uppercase tracking-wider text-slate-500">
                AI Prep Platform
              </p>
            </div>
          </div>
        </div>

        <nav className="relative flex-1 space-y-5 overflow-y-auto px-3 py-5">
          {navSections.map((section) => (
            <div key={section.title}>
              <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                {section.title}
              </p>
              <div className="space-y-0.5">
                {section.items.map(({ to, icon: Icon, label }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={to === '/'}
                    className={({ isActive }) =>
                      `group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                        isActive
                          ? 'bg-gradient-to-r from-violet-600/25 to-cyan-600/10 text-white shadow-inner shadow-violet-900/20'
                          : 'text-slate-400 hover:bg-white/5 hover:text-slate-100'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <span
                          className={`flex h-8 w-8 items-center justify-center rounded-lg transition-colors ${
                            isActive
                              ? 'bg-violet-500/20 text-violet-300'
                              : 'bg-white/5 text-slate-500 group-hover:bg-white/8 group-hover:text-slate-300'
                          }`}
                        >
                          <Icon size={16} />
                        </span>
                        <span>{label}</span>
                        {isActive && (
                          <span className="ml-auto h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
                        )}
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="relative border-t border-white/8 p-4">
          <div className="mb-3 flex items-center gap-3 rounded-xl bg-white/5 px-3 py-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-xs font-bold text-white">
              {userInitials(user?.full_name)}
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">{user?.full_name}</p>
              <p className="truncate text-xs text-slate-500">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/8 bg-white/5 px-3 py-2.5 text-sm font-medium text-slate-300 transition hover:border-red-500/30 hover:bg-red-500/10 hover:text-red-300"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      <main className="ml-64 flex-1 p-8">
        <Outlet />
      </main>
    </div>
  )
}