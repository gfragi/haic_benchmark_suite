import { Link, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Home, LayoutList, GitCompare, Upload, BookOpen, Activity, Compass, HelpCircle, ClipboardList } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'
import { RELEASES } from '../releaseNotes'
import humaineLogo from '../assets/humaine-logo.webp'
import huaLogo from '../assets/hua-logo.png'
import humaineIcon from '../assets/humaine-icon.png'
import huaIcon from '../assets/hua-icon.png'

// Keep in sync with PUBLIC_PATHS in src/main.jsx - these are the only sidebar
// items reachable without logging in.
const NAV_TOP = [
  { label: 'Home',              href: '/',                icon: Home,          exact: true, public: true },
  { label: 'Getting Started',   href: '/getting-started', icon: HelpCircle,                 public: true },
]

const NAV_SECTIONS = [
  {
    heading: 'Pilots',
    items: [
      { label: 'Evaluations',  href: '/configs',   icon: LayoutList },
      { label: 'New Pilot',    href: '/pilot/new', icon: Compass    },
      { label: 'Ingest Logs',  href: '/ingest',    icon: Upload     },
    ],
  },
  {
    heading: 'Analysis',
    items: [
      { label: 'Compare Versions',  href: '/compare', icon: GitCompare              },
      { label: 'Submit Survey',     href: '/survey',  icon: ClipboardList           },
      { label: 'Metrics Reference', href: '/metrics', icon: BookOpen, public: true  },
    ],
  },
]

function NavItem({ label, href, icon: Icon, exact, public: isPublic, location }) {
  const active = exact
    ? location.pathname === href
    : location.pathname.startsWith(href)
  return (
    <Link
      to={href}
      className={clsx(
        'flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition-colors',
        active
          ? 'bg-indigo-50 text-indigo-700'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
      )}
    >
      <Icon size={15} className={active ? 'text-indigo-600' : 'text-gray-400'} />
      <span className="flex-1">{label}</span>
      {isPublic && (
        <span
          className="text-[10px] font-medium text-gray-400 bg-gray-100 rounded px-1.5 py-0.5"
          title="Accessible without logging in"
        >
          public
        </span>
      )}
    </Link>
  )
}

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
        </Link>
        {RELEASES[0]?.version && (
          <Link
            to="/releases"
            className="text-xs text-gray-400 hover:text-indigo-600 font-mono transition-colors"
            title="Release notes"
          >
            {RELEASES[0].version}
          </Link>
        )}
        <div className="ml-auto flex items-center gap-3">
          <img src={humaineIcon} alt="humAIne" className="h-7 w-7 object-contain" />
          <img src={huaIcon} alt="Harokopio University" className="h-7 w-7 object-contain" />
          <HealthDot />
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-52 bg-white border-r border-gray-200 flex-shrink-0 flex flex-col pt-4 pb-4">
          <nav className="px-3 space-y-4 flex-1">
            <div className="space-y-0.5">
              {NAV_TOP.map((item) => <NavItem key={item.href} {...item} location={location} />)}
            </div>
            {NAV_SECTIONS.map(({ heading, items }) => (
              <div key={heading}>
                <p className="px-3 pb-1 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">
                  {heading}
                </p>
                <div className="space-y-0.5">
                  {items.map((item) => <NavItem key={item.href} {...item} location={location} />)}
                </div>
              </div>
            ))}
          </nav>

          {/* Sidebar footer */}
          <div className="px-4 pt-4 border-t border-gray-100 space-y-3">
            <img src={humaineLogo} alt="humAIne" className="h-10 w-auto max-w-full object-contain" />
            <img src={huaLogo} alt="Harokopio University" className="h-10 w-auto max-w-full object-contain" />
            <p className="text-xs text-gray-400">© 2026 humAIne</p>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  )
}
