import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { claimCase, getTrail, readSession } from "../api/client"
import Header from "../components/Header"

export default function CaseDetails() {
  const { caseId } = useParams()
  const navigate = useNavigate()
  const session = readSession()
  const token = session?.access_token ?? ""
  const [trail, setTrail] = useState(null)
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
    getTrail(caseId)
      .then((body) => {
        if (!cancelled) {
          setTrail(body)
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
  }, [token, caseId])

  async function onClaim() {
    setError("")
    try {
      await claimCase(caseId)
      navigate("/cases")
    } catch (err) {
      setError(err.message)
    }
  }

  if (!token) {
    return null
  }

  return (
    <>
      <Header />
      <main>
        <p>
          <Link to="/cases">Back to cases</Link>
        </p>
        <h1>Location trail</h1>
        {error ? <p className="error">{error}</p> : null}
        {trail ? (
          <>
            <p>
              VIN <strong>{trail.vin}</strong>
            </p>
            <table>
              <thead>
                <tr>
                  <th>Seen at</th>
                  <th>Plate</th>
                  <th>Latitude</th>
                  <th>Longitude</th>
                  <th>Camera</th>
                </tr>
              </thead>
              <tbody>
                {trail.scans.map((scan) => (
                  <tr key={scan.id}>
                    <td>{new Date(scan.scanned_at).toLocaleString()}</td>
                    <td>{scan.plate}</td>
                    <td>{scan.latitude}</td>
                    <td>{scan.longitude}</td>
                    <td>{scan.camera_id}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {trail.status === "pending_claim" ? (
              <button type="button" onClick={onClaim}>
                Claim
              </button>
            ) : null}
          </>
        ) : null}
      </main>
    </>
  )
}
