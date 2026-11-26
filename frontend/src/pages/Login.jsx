import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { login, saveSession } from "../api/client"

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState("agent.a")
  const [password, setPassword] = useState("demo-pass")
  const [error, setError] = useState("")

  async function onSubmit(event) {
    event.preventDefault()
    setError("")
    try {
      const session = await login(username, password)
      saveSession(session)
      navigate("/cases")
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="narrow">
      <h1>Recovery desk</h1>
      <p>Sign in as a staff member of one agency. The tenant comes from the account, not from this form.</p>
      <form onSubmit={onSubmit}>
        <label>
          Username
          <input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
          />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit">Sign in</button>
      </form>
      <p className="hint">Demo accounts: agent.a and agent.b, password demo-pass.</p>
    </main>
  )
}
