import { Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './layout/AppShell'
import ConfigListPage from './pages/ConfigListPage'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Navigate to="/configs" replace />} />
        <Route path="/configs" element={<ConfigListPage />} />
        {/* Phase 2 */}
        <Route
          path="/config/:id/results"
          element={
            <div className="p-6 text-gray-400 text-sm">
              Results Dashboard — Phase 2
            </div>
          }
        />
        {/* Phase 3 */}
        <Route
          path="/compare"
          element={
            <div className="p-6 text-gray-400 text-sm">
              Version Comparison — Phase 3
            </div>
          }
        />
        {/* Phase 4 */}
        <Route
          path="/ingest"
          element={
            <div className="p-6 text-gray-400 text-sm">
              Log Ingest Wizard — Phase 4
            </div>
          }
        />
      </Routes>
    </AppShell>
  )
}
