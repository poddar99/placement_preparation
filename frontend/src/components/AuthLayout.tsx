import { Rocket } from 'lucide-react'
import type { ReactNode } from 'react'

interface AuthLayoutProps {
  title: string
  subtitle: string
  children: ReactNode
  footer: ReactNode
}

export default function AuthLayout({ title, subtitle, children, footer }: AuthLayoutProps) {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0d0f14] px-4 py-10">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-24 top-1/4 h-72 w-72 rounded-full bg-violet-600/25 blur-3xl" />
        <div className="absolute -right-20 bottom-1/4 h-64 w-64 rounded-full bg-cyan-500/15 blur-3xl" />
        <div className="absolute left-1/2 top-0 h-48 w-96 -translate-x-1/2 rounded-full bg-indigo-600/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 to-cyan-500 text-white shadow-xl shadow-violet-900/50">
            <Rocket size={28} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">PlacementPilot</h1>
          <p className="mt-1 text-xs font-semibold uppercase tracking-widest text-slate-500">
            AI Prep Platform
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#161922]/90 p-8 shadow-2xl shadow-black/40 backdrop-blur-xl">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-white">{title}</h2>
            <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
          </div>

          {children}

          <div className="mt-6 text-center text-sm text-slate-400">{footer}</div>
        </div>
      </div>
    </div>
  )
}

export const authInputClass =
  'w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-slate-500 transition focus:border-violet-500/50 focus:bg-white/8 focus:outline-none focus:ring-2 focus:ring-violet-500/20'

export const authLabelClass = 'mb-1.5 block text-sm font-medium text-slate-300'

export const authButtonClass =
  'flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-900/30 transition hover:-translate-y-0.5 hover:shadow-xl disabled:translate-y-0 disabled:opacity-50 disabled:shadow-none'

export const authLinkClass = 'font-semibold text-cyan-400 transition hover:text-cyan-300'