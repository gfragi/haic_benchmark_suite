export default function RequireAuth({ children }) {
  if (!window.__kc?.authenticated) {
    window.__kc?.login()
    return null
  }
  return children
}
