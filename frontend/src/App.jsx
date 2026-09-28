import { useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import ResearchChat from './pages/ResearchChat'
import MultiPaperSynthesis from './pages/MultiPaperSynthesis'

function App() {
  const [documents, setDocuments] = useState([])
  const addDocument = (document) => setDocuments((current) => [document, ...current])

  return <BrowserRouter><div className="app-shell"><Navbar /><div className="app-body"><Sidebar /><main className="main-content"><Routes>
    <Route path="/" element={<Dashboard documentCount={documents.length} />} />
    <Route path="/documents" element={<Documents documents={documents} onUploaded={addDocument} />} />
    <Route path="/chat" element={<ResearchChat />} />
    <Route path="/synthesis" element={<MultiPaperSynthesis />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></main></div></div></BrowserRouter>
}

export default App