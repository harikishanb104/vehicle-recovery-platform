import { BrowserRouter, Route, Routes } from "react-router-dom"
import CaseDetails from "./pages/CaseDetails"
import Cases from "./pages/Cases"
import Login from "./pages/Login"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/cases" element={<Cases />} />
        <Route path="/cases/:caseId" element={<CaseDetails />} />
      </Routes>
    </BrowserRouter>
  )
}
