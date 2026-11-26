import { clearSession, readSession } from "../api/client"

export default function Header() {
  const session = readSession()

  function logout() {
    clearSession()
    window.location.assign("/")
  }

  return (
    <header className="top">
      <div>
        <p className="eyebrow">Plate scan</p>
        <strong>{session?.user?.username}</strong>
      </div>
      <button type="button" onClick={logout}>
        Log out
      </button>
    </header>
  )
}
