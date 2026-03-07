import { NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, Briefcase, Users, GitBranch, BarChart3, Radar, Search } from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/jobs', icon: Briefcase, label: 'Jobs' },
  { to: '/candidates', icon: Users, label: 'Candidates' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/scrape', icon: Search, label: 'Source' },
]

export default function Layout({ children }) {
  return (
    <div className="flex min-h-screen bg-dark-900">
      {/* Sidebar */}
      <aside className="w-64 bg-dark-800 border-r border-dark-700 flex flex-col fixed h-full z-20">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-dark-700">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-600 to-teal-500 flex items-center justify-center">
              <Radar size={18} className="text-white" />
            </div>
            <div>
              <div className="text-white font-bold text-base leading-none">TalentRadar</div>
              <div className="text-brand-500 text-xs mt-0.5">AI Platform</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-600/20 text-brand-400 border border-brand-600/30'
                  : 'text-gray-400 hover:text-gray-100 hover:bg-dark-700'
              )}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-dark-700">
          <div className="text-xs text-gray-500">TalentRadar AI v1.0</div>
          <div className="text-xs text-green-500 mt-0.5">● System Online</div>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-64 flex-1 min-h-screen">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
