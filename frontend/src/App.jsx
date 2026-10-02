import { useCallback, useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import './App.css'
import { getCurrentUser } from './api/authApi'
import { getDocuments } from './api/documentsApi'
import { chatWithResearch, getChatHistory } from './api/chatApi'
import { getFriendlyError } from './api/errors'
import { getSynthesisHistory, synthesizePapers } from './api/synthesisApi'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import ErrorMessage from './components/ErrorMessage'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import AuthPage from './pages/AuthPage'
import ResearchChat from './pages/ResearchChat'
import MultiPaperSynthesis from './pages/MultiPaperSynthesis'

function AppContent() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [authReady, setAuthReady] = useState(
    () => !localStorage.getItem('research_access_token'),
  )
  const [documents, setDocuments] = useState([])
  const [documentsError, setDocumentsError] = useState('')
  const [chatQuestion, setChatQuestion] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)
  const [chatError, setChatError] = useState('')
  const [synthesisQuestion, setSynthesisQuestion] = useState('')
  const [synthesisResult, setSynthesisResult] = useState(null)
  const [synthesisHistory, setSynthesisHistory] = useState([])
  const [synthesisLoading, setSynthesisLoading] = useState(false)
  const [synthesisError, setSynthesisError] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('research_access_token')
    if (!token) return undefined

    let cancelled = false
    getCurrentUser()
      .then((currentUser) => {
        if (!cancelled) setUser(currentUser)
      })
      .catch(() => {
        localStorage.removeItem('research_access_token')
      })
      .finally(() => {
        if (!cancelled) setAuthReady(true)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const clearWorkspace = useCallback(() => {
    setDocuments([])
    setDocumentsError('')
    setChatQuestion('')
    setChatMessages([])
    setChatError('')
    setSynthesisQuestion('')
    setSynthesisResult(null)
    setSynthesisHistory([])
    setSynthesisError('')
  }, [])

  const handleSessionExpired = useCallback(() => {
    localStorage.removeItem('research_access_token')
    setUser(null)
    clearWorkspace()
    navigate('/login', { replace: true })
  }, [clearWorkspace, navigate])

  useEffect(() => {
    window.addEventListener('research:session-expired', handleSessionExpired)
    return () => window.removeEventListener('research:session-expired', handleSessionExpired)
  }, [handleSessionExpired])

  useEffect(() => {
    if (!user) return undefined

    let cancelled = false
    getDocuments()
      .then((items) => {
        if (!cancelled) {
          setDocuments(items)
          setDocumentsError('')
        }
      })
      .catch((error) => {
        if (!cancelled) setDocumentsError(getFriendlyError(error))
      })

    getChatHistory()
      .then((history) => {
        if (!cancelled) {
          setChatMessages(history.flatMap((item) => [
            { role: 'user', content: item.question, id: `${item.id}-question` },
            { role: 'ai', answer: item.answer, sources: item.sources, id: `${item.id}-answer` },
          ]))
        }
      })
      .catch((error) => {
        if (!cancelled) setChatError(getFriendlyError(error))
      })

    getSynthesisHistory()
      .then((history) => {
        if (!cancelled) setSynthesisHistory(history)
      })
      .catch((error) => {
        if (!cancelled) setSynthesisError(getFriendlyError(error))
      })

    return () => {
      cancelled = true
    }
  }, [user])

  const handleAuthenticated = (session) => {
    localStorage.setItem('research_access_token', session.access_token)
    clearWorkspace()
    setUser(session.user)
    setAuthReady(true)
    navigate('/', { replace: true })
  }

  const handleLogout = () => {
    localStorage.removeItem('research_access_token')
    clearWorkspace()
    setUser(null)
    navigate('/login', { replace: true })
  }

  const refreshDocuments = useCallback(async () => {
    try {
      setDocuments(await getDocuments())
      setDocumentsError('')
    } catch (error) {
      setDocumentsError(getFriendlyError(error))
    }
  }, [])

  const submitChatQuestion = async () => {
    const question = chatQuestion.trim()
    if (!question || chatLoading) return

    setChatLoading(true)
    setChatError('')
    try {
      const result = await chatWithResearch(question)
      setChatMessages((current) => [
        ...current,
        { role: 'user', content: question },
        { role: 'ai', answer: result.answer, sources: result.sources },
      ])
      setChatQuestion('')
    } catch (error) {
      setChatError(getFriendlyError(error))
    } finally {
      setChatLoading(false)
    }
  }

  const submitSynthesisQuestion = async () => {
    const question = synthesisQuestion.trim()
    if (!question || synthesisLoading) return

    setSynthesisLoading(true)
    setSynthesisError('')
    try {
      const result = await synthesizePapers(question)
      setSynthesisResult(result)
      setSynthesisHistory((current) => [
        { ...result, id: `current-${Date.now()}` },
        ...current,
      ])
    } catch (error) {
      setSynthesisError(getFriendlyError(error))
    } finally {
      setSynthesisLoading(false)
    }
  }

  if (!authReady) {
    return <main className="auth-page"><p>Restoring your secure session...</p></main>
  }

  return <Routes>
    <Route path="/login" element={<AuthPage mode="login" user={user} onAuthenticated={handleAuthenticated} />} />
    <Route path="/register" element={<AuthPage mode="register" user={user} onAuthenticated={handleAuthenticated} />} />
    <Route path="*" element={user
      ? <div className="app-shell">
        <Navbar user={user} onLogout={handleLogout} />
        <div className="app-body">
          <Sidebar />
          <main className="main-content">
            <ErrorMessage message={documentsError} />
            <Routes>
              <Route path="/" element={<Dashboard documentCount={documents.length} />} />
              <Route path="/documents" element={<Documents documents={documents} onUploaded={refreshDocuments} onDeleted={refreshDocuments} />} />
              <Route path="/chat" element={<ResearchChat question={chatQuestion} onQuestionChange={setChatQuestion} messages={chatMessages} loading={chatLoading} error={chatError} onSubmit={submitChatQuestion} />} />
              <Route path="/synthesis" element={<MultiPaperSynthesis question={synthesisQuestion} onQuestionChange={setSynthesisQuestion} result={synthesisResult} history={synthesisHistory} loading={synthesisLoading} error={synthesisError} onSelectHistory={(item) => { setSynthesisQuestion(item.question); setSynthesisResult(item) }} onSubmit={submitSynthesisQuestion} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
      : <Navigate to="/login" replace />}
    />
  </Routes>
}

function App() {
  return <BrowserRouter><AppContent /></BrowserRouter>
}

export default App
