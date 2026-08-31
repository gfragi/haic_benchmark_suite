import { Routes, Route } from 'react-router-dom'
import AppShell from './layout/AppShell'
import RequireAuth from './components/RequireAuth'
import HomePage from './pages/HomePage'
import ConfigListPage from './pages/ConfigListPage'
import ResultsDashboardPage from './pages/ResultsDashboardPage'
import CompareVersionsPage from './pages/CompareVersionsPage'
import LogWizardPage from './pages/LogWizardPage'
import SimulatePage from './pages/SimulatePage'
import MetricsGlossaryPage from './pages/MetricsGlossaryPage'
import PilotOnboardingPage from './pages/PilotOnboardingPage'
import GettingStartedPage from './pages/GettingStartedPage'
import SurveyPage from './pages/SurveyPage'
import PublicSurveyPage from './pages/PublicSurveyPage'
import SurveyDetailPage from './pages/SurveyDetailPage'
import ReleaseNotesPage from './pages/ReleaseNotesPage'

export default function App() {
  return (
    <Routes>
      <Route path="/public/survey" element={<PublicSurveyPage />} />
      <Route
        path="*"
        element={(
          <AppShell>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/configs" element={<RequireAuth><ConfigListPage /></RequireAuth>} />
              <Route path="/config/:id/results" element={<RequireAuth><ResultsDashboardPage /></RequireAuth>} />
              <Route path="/config/:id/survey-details" element={<RequireAuth><SurveyDetailPage /></RequireAuth>} />
              <Route path="/compare" element={<RequireAuth><CompareVersionsPage /></RequireAuth>} />
              <Route path="/ingest" element={<RequireAuth><LogWizardPage /></RequireAuth>} />
              <Route path="/simulate" element={<RequireAuth><SimulatePage /></RequireAuth>} />
              <Route path="/metrics" element={<MetricsGlossaryPage />} />
              <Route path="/releases" element={<ReleaseNotesPage />} />
              <Route path="/pilot/new" element={<RequireAuth><PilotOnboardingPage /></RequireAuth>} />
              <Route path="/getting-started" element={<GettingStartedPage />} />
              <Route path="/survey" element={<RequireAuth><SurveyPage /></RequireAuth>} />
            </Routes>
          </AppShell>
        )}
      />
    </Routes>
  )
}
