import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import JobDetail from './pages/JobDetail'
import Candidates from './pages/Candidates'
import CandidateDetail from './pages/CandidateDetail'
import Pipeline from './pages/Pipeline'
import Analytics from './pages/Analytics'
import Scrape from './pages/Scrape'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
        <Route path="/candidates" element={<Candidates />} />
        <Route path="/candidates/:id" element={<CandidateDetail />} />
        <Route path="/pipeline/:jobId" element={<Pipeline />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/scrape" element={<Scrape />} />
      </Routes>
    </Layout>
  )
}
