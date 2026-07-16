export default function RequireAuth({ children }) {
  if (!window.__kc?.authenticated) {
    window.__kc?.login()
    // Shown briefly while the Keycloak redirect kicks in, instead of a blank
    // page - also covers the case where window.__kc isn't initialized yet
    // and login() is a no-op, so the user isn't left staring at nothing.
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-2 text-sm text-gray-400">
        <p>Sign in required</p>
        <p className="text-xs text-gray-300">Redirecting to login…</p>
      </div>
    )
  }
  return children
}
