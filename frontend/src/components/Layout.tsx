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
  User,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/dsa', icon: Code2, label: 'DSA Tracker' },
  { to: '/resume', icon: FileText, label: 'Resume Analyzer' },
  { to: '/resume-rewrite', icon: PenLine, label: 'Resume Rewriter' },
  { to: '/mentor', icon: Bot, label: 'AI Mentor' },
  { to: '/companies', icon: Building2, label: 'Company Prep' },
  { to: '/interview', icon: MessageSquare, label: 'Interview RAG' },
  { to: '/mock-interview', icon: Mic, label: 'Mock Interview' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/profile', icon: User, label: 'Profile' },
]

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col bg-primary text-white shadow-xl">
        <div className="border-b border-white/10 px-6 py-5">
          <h1 className="text-lg font-bold tracking-tight">PlacementPilot AI</h1>
          <p className="mt-1 text-xs text-white/60">Placement preparation platform</p>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-white/15 text-white'
                    : 'text-white/70 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 px-4 py-4">
          <p className="truncate text-sm font-medium">{user?.full_name}</p>
          <p className="truncate text-xs text-white/50">{user?.email}</p>
          <button
            onClick={logout}
            className="mt-3 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-white/70 transition-colors hover:bg-white/10 hover:text-white"
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