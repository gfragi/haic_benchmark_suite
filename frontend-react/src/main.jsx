import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import keycloak from './services/keycloak'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
})

// These stay public even when not authenticated — keep in sync with the
// route wrapping in App.jsx.
const PUBLIC_PATHS = ['/', '/getting-started', '/metrics', '/public/survey']
const isPublicPath = () => PUBLIC_PATHS.includes(window.location.pathname)

const publicRedirect = () =>
  window.location.origin + window.location.pathname + window.location.search

const mountApp = () => {
  createRoot(document.getElementById('root')).render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </StrictMode>,
  )
}

if (import.meta.env.VITE_BYPASS_AUTH === 'true') {
  console.warn('Auth bypass enabled — skipping Keycloak')
  window.__kc = { authenticated: true, token: 'dev-token', tokenParsed: { preferred_username: 'dev-user' } }
  mountApp()
} else {
  keycloak
    .init({
      onLoad: isPublicPath() ? 'check-sso' : 'login-required',
      checkLoginIframe: false,
      redirectUri: isPublicPath()
        ? publicRedirect()
        : window.location.origin + '/',
    })
    .then((authenticated) => {
      console.log('Keycloak init resolved:', authenticated)
      window.__kc = keycloak
      if (!authenticated && !isPublicPath()) {
        console.warn('Not authenticated, redirecting to login')
        keycloak.login()
        return
      }
      mountApp()
    })
    .catch((err) => {
      console.error('Keycloak init failed:', err)
    })
}
