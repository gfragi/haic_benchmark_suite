import { Link, useLocation } from 'react-router-dom'
import { LayoutList, GitCompare, Upload, Activity } from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { label: 'Configurations', href: '/configs', icon: LayoutList },
  { label: 'Compare Versions', href: '/compare', icon: GitCompare },
  { label: 'Ingest Logs', href: '/ingest', icon: Upload },
]

export default function AppShell({ children }) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top nav */}
      <header className="bg-white border-b border-gray-200 h-14 flex items-center px-6 gap-3 flex-shrink-0 shadow-sm">
        <Activity size={18} className="text-indigo-600" />
        <span className="font-semibold text-gray-900 text-sm">
          HAIC Benchmark Suite
        </span>
        <span className="text-xs text-gray-400 font-mono ml-1">v2.0</span>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-52 bg-white border-r border-gray-200 flex-shrink-0 pt-4 pb-8">
          <nav className="px-3 space-y-0.5">
            {NAV.map(({ label, href, icon: Icon }) => {
              const active = location.pathname.startsWith(href)
              return (
                <Link
                  key={href}
                  to={href}
                  className={clsx(
                    'flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    active
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
                  )}
                >
                  <Icon size={15} className={active ? 'text-indigo-600' : 'text-gray-400'} />
                  {label}
                </Link>
              )
            })}
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  )
}
