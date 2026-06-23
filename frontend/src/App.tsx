import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import AiMentor from './pages/AiMentor'
import Analytics from './pages/Analytics'
import CompanyPrep from './pages/CompanyPrep'
import Dashboard from './pages/Dashboard'
import DsaTracker from './pages/DsaTracker'
import InterviewRag from './pages/InterviewRag'
import Login from './pages/Login'
import MockInterview from './pages/MockInterview'
import Profile from './pages/Profile'
import Register from './pages/Register'
import ResumeAnalyzer from './pages/ResumeAnalyzer'
import ResumeRewriter from './pages/ResumeRewriter'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="dsa" element={<DsaTracker />} />
            <Route path="resume" element={<ResumeAnalyzer />} />
            <Route path="resume-rewrite" element={<ResumeRewriter />} />
            <Route path="mentor" element={<AiMentor />} />
            <Route path="companies" element={<CompanyPrep />} />
            <Route path="interview" element={<InterviewRag />} />
            <Route path="mock-interview" element={<MockInterview />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="profile" element={<Profile />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}