import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  LayoutList, Upload, BarChart2, GitCompare,
  BookOpen, ChevronRight, Loader2, ArrowRight,
} from 'lucide-react'
import { api } from '../services/api'

const STEPS = [
  {
    n: 1,
    title: 'Configure',
    desc: 'Create an evaluation configuration with your AI model details and target metrics.',
    href: '/configs',
    icon: LayoutList,
    action: 'Go to Configurations',
  },
  {
    n: 2,
    title: 'Ingest Logs',
    desc: 'Upload interaction logs or register a log source. Validate schema and field coverage.',
    href: '/ingest',
    icon: Upload,
    action: 'Open Log Wizard',
  },
  {
    n: 3,
    title: 'View Results',
    desc: 'Trigger evaluation, explore HAIC metrics, and compare AI model versions side-by-side.',
    href: '/configs',
    icon: BarChart2,
    action: 'Browse Results',
  },
]

const QUICK_LINKS = [
  { label: 'Compare Versions', href: '/compare', icon: GitCompare },
  { label: 'Ingest Logs', href: '/ingest', icon: Upload },
  { label: 'Metrics Reference', href: '/metrics', icon: BookOpen },
]

export default function HomePage() {
  const { data: configs, isLoading } = useQuery({
    queryKey: ['configs'],
    queryFn: () => api.configs.list(),
  })

  const recent = (configs ?? []).slice(0, 5)

  return (
    <div className="space-y-10 max-w-3xl">

      {/* Hero */}
      <div className="bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-xl p-8">
        <p className="text-xs font-semibold text-indigo-500 uppercase tracking-wider mb-2">
          Human-AI Collaboration
        </p>
        <h1 className="text-2xl font-bold text-gray-900 leading-tight">
          HAIC Benchmark Suite
        </h1>
        <p className="mt-2 text-sm text-gray-500 max-w-xl leading-relaxed">
          Benchmark, compare, and improve Human-AI Collaboration across multiple
          evaluation dimensions — from trust and cognitive load to efficiency and adaptability.
        </p>
        <div className="mt-5 flex gap-3">
          <Link
            to="/configs"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors"
          >
            Start Evaluation <ArrowRight size={14} />
          </Link>
          <Link
            to="/metrics"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 bg-white text-gray-700 text-sm font-medium hover:border-indigo-300 hover:text-indigo-700 transition-colors"
          >
            <BookOpen size={14} /> Metrics Reference
          </Link>
        </div>
      </div>

      {/* Workflow steps */}
      <section>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          How it works
        </h2>
        <div className="grid grid-cols-3 gap-4">
          {STEPS.map(({ n, title, desc, href, icon: Icon, action }) => (
            <Link
              key={n}
              to={href}
              className="group bg-white rounded-lg border border-gray-200 p-4
                         hover:border-indigo-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-mono font-bold text-gray-200">
                  {String(n).padStart(2, '0')}
                </span>
                <Icon size={14} className="text-indigo-500" />
              </div>
              <p className="text-sm font-semibold text-gray-800 group-hover:text-indigo-700">
                {title}
              </p>
              <p className="text-xs text-gray-500 mt-1 leading-relaxed">{desc}</p>
              <p className="text-xs text-indigo-500 mt-3 flex items-center gap-1
                            opacity-0 group-hover:opacity-100 transition-opacity">
                {action} <ChevronRight size={11} />
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* Recent configurations */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Recent Configurations
          </h2>
          <Link
            to="/configs"
            className="text-xs text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
          >
            View all <ChevronRight size={12} />
          </Link>
        </div>

        {isLoading ? (
          <div className="flex items-center gap-2 text-gray-400 text-sm py-4">
            <Loader2 size={14} className="animate-spin" /> Loading…
          </div>
        ) : recent.length === 0 ? (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-700">
            No configurations yet.{' '}
            <Link to="/configs" className="underline font-medium">
              Create your first one
            </Link>
            .
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
            {recent.map(c => (
              <Link
                key={c.id}
                to={`/config/${c.id}/results`}
                className="flex items-center justify-between px-4 py-3
                           hover:bg-gray-50 transition-colors group"
              >
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-800 group-hover:text-indigo-700 truncate">
                    {c.application_name}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {c.ai_model_name}
                    {c.config_type ? ` · ${c.config_type}` : ''}
                  </p>
                </div>
                <ChevronRight size={14} className="text-gray-300 group-hover:text-indigo-400 flex-shrink-0" />
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Quick links */}
      <section>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Quick Actions
        </h2>
        <div className="flex gap-3 flex-wrap">
          {QUICK_LINKS.map(({ label, href, icon: Icon }) => (
            <Link
              key={href}
              to={href}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200
                         bg-white text-sm text-gray-700 hover:border-indigo-300 hover:text-indigo-700
                         transition-colors"
            >
              <Icon size={14} /> {label}
            </Link>
          ))}
        </div>
      </section>

    </div>
  )
}
