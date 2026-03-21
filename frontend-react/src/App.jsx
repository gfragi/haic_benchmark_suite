import { Routes, Route } from 'react-router-dom'
import AppShell from './layout/AppShell'
import HomePage from './pages/HomePage'
import ConfigListPage from './pages/ConfigListPage'
import ResultsDashboardPage from './pages/ResultsDashboardPage'
import CompareVersionsPage from './pages/CompareVersionsPage'
import LogWizardPage from './pages/LogWizardPage'
import MetricsGlossaryPage from './pages/MetricsGlossaryPage'
import PilotOnboardingPage from './pages/PilotOnboardingPage'
import GettingStartedPage from './pages/GettingStartedPage'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/configs" element={<ConfigListPage />} />
        <Route path="/config/:id/results" element={<ResultsDashboardPage />} />
        <Route path="/compare" element={<CompareVersionsPage />} />
        <Route path="/ingest" element={<LogWizardPage />} />
        <Route path="/metrics" element={<MetricsGlossaryPage />} />
        <Route path="/pilot/new" element={<PilotOnboardingPage />} />
        <Route path="/getting-started" element={<GettingStartedPage />} />
      </Routes>
    </AppShell>
  )
}
