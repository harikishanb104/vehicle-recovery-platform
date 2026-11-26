import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { claimCase, listCases, readSession } from "../api/client"
import Header from "../components/Header"

const filters = [
  { value: "", label: "All visible" },
  { value: "pending_claim", label: "Pending claim" },
  { value: "active", label: "Active" },
  { value: "closed", label: "Closed" },
]

export default function Cases() {
  const navigate = useNavigate()
  const session = readSession()
  const token = session?.access_token ?? ""
  const tenantId = session?.user?.tenant_id
  const [status, setStatus] = useState("")
  const [cases, setCases] = useState([])
  const [error, setError] = useState("")

  useEffect(() => {
    if (!token) {
      navigate("/")
    }
  }, [token, navigate])

  useEffect(() => {
    if (!token) {
      return
    }
    let cancelled = false
    listCases(status)
      .then((rows) => {
        if (!cancelled) {
          setCases(rows)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message)
        }
      })
    return () => {
      cancelled = true
    }
  }, [token, status])

  async function onClaim(caseId) {
    setError("")
    try {
      await claimCase(caseId)
      setCases(await listCases(status))
    } catch (err) {
      setError(err.message)
    }
  }

  if (!token) {
    return null
  }

  const mine = cases.filter((row) => row.tenant_id === tenantId)
  const claimable = cases.filter((row) => row.status === "pending_claim")

  return (
    <>
      <Header />
      <main>
        <div className="title-row">
          <h1>Cases</h1>
          <label>
            Status
            <select value={status} onChange={(event) => setStatus(event.target.value)}>
              {filters.map((filter) => (
                <option key={filter.value} value={filter.value}>
                  {filter.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        {error ? <p className="error">{error}</p> : null}
        <section>
          <h2>My cases</h2>
          <CaseTable rows={mine} empty="No cases for this agency in the current filter." />
        </section>
        <section>
          <h2>Available to claim</h2>
          <p>Pending cases are visible to every agency until one of them claims.</p>
          <CaseTable
            rows={claimable}
            empty="No pending cases."
            onClaim={onClaim}
          />
        </section>
      </main>
    </>
  )
}

function CaseTable({ rows, empty, onClaim }) {
  if (rows.length === 0) {
    return <p className="empty">{empty}</p>
  }
  return (
    <table>
      <thead>
        <tr>
          <th>VIN</th>
          <th>Status</th>
          <th>Opened</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <td>{row.vin}</td>
            <td>{labelStatus(row.status)}</td>
            <td>{new Date(row.created_at).toLocaleString()}</td>
            <td className="actions">
              <Link to={`/cases/${row.id}`}>Trail</Link>
              {onClaim && row.status === "pending_claim" ? (
                <button type="button" onClick={() => onClaim(row.id)}>
                  Claim
                </button>
              ) : null}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function labelStatus(status) {
  if (status === "pending_claim") {
    return "Pending claim"
  }
  if (status === "active") {
    return "Active"
  }
  return "Closed"
}
