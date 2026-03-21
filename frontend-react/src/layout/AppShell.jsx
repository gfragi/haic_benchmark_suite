import { Link, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Home, LayoutList, GitCompare, Upload, BookOpen, Activity } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

const NAV = [
  { label: 'Home',              href: '/',        icon: Home,       exact: true },
  { label: 'Configurations',    href: '/configs', icon: LayoutList  },
  { label: 'Compare Versions',  href: '/compare', icon: GitCompare  },
  { label: 'Ingest Logs',       href: '/ingest',  icon: Upload      },
  { label: 'Metrics Reference', href: '/metrics', icon: BookOpen    },
]

function HealthDot() {
  const { data, isError } = useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    refetchInterval: 30_000,
    retry: false,
    staleTime: 20_000,
  })
  const ok = !isError && data?.status === 'ok'
  return (
    <div className="flex items-center gap-1.5">
      <span className={clsx('w-1.5 h-1.5 rounded-full', ok ? 'bg-green-400' : 'bg-amber-400')} />
      <span className="text-xs text-gray-400">{ok ? 'Online' : 'Offline'}</span>
    </div>
  )
}

export default function AppShell({ children }) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top nav */}
      <header className="bg-white border-b border-gray-200 h-14 flex items-center px-6 gap-3 flex-shrink-0 shadow-sm">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <Activity size={18} className="text-indigo-600" />
          <span className="font-semibold text-gray-900 text-sm">HAIC Benchmark Suite</span>
          <span className="text-xs text-gray-400 font-mono ml-0.5">v2.0</span>
        </Link>
        <div className="ml-auto">
          <HealthDot />
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-52 bg-white border-r border-gray-200 flex-shrink-0 flex flex-col pt-4 pb-4">
          <nav className="px-3 space-y-0.5 flex-1">
            {NAV.map(({ label, href, icon: Icon, exact }) => {
              const active = exact
                ? location.pathname === href
                : location.pathname.startsWith(href)
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

          {/* Sidebar footer */}
          <div className="px-6 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-400">© 2025 humAIne</p>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  )
}
