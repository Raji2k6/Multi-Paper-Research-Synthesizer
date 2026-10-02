import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { loginAccount, registerAccount } from '../api/authApi'
import { getFriendlyError } from '../api/errors'
import ErrorMessage from '../components/ErrorMessage'
import BrandMark from '../components/BrandMark'

export default function AuthPage({ mode, user, onAuthenticated }) {
  const isRegister = mode === 'register'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) return <Navigate to="/" replace />

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const result = isRegister
        ? await registerAccount({ name, email, password })
        : await loginAccount({ email, password })
      onAuthenticated(result)
    } catch (requestError) {
      setError(getFriendlyError(requestError))
    } finally {
      setLoading(false)
    }
  }

  return <main className="auth-page">
    <section className="panel auth-panel">
      <div className="brand auth-brand"><BrandMark /><span className="brand-title">PaperFusion AI<span className="brand-subtitle">Your research, connected</span></span></div>
      <span className="eyebrow">Private research workspace</span>
      <h1>{isRegister ? 'Create your account' : 'Welcome back'}</h1>
      <p className="panel-subtitle">{isRegister ? 'Your papers and research history are saved to your account.' : 'Sign in to continue to your saved papers and research.'}</p>
      <form className="auth-form" onSubmit={submit}>
        {isRegister && <label className="auth-field">
          <span>Name</span>
          <input autoComplete="name" required maxLength={100} value={name} onChange={(event) => setName(event.target.value)} />
        </label>}
        <label className="auth-field">
          <span>Email</span>
          <input type="email" autoComplete="email" required maxLength={320} value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label className="auth-field">
          <span>Password</span>
          <input type="password" autoComplete={isRegister ? 'new-password' : 'current-password'} required minLength={isRegister ? 8 : 1} maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} />
          {isRegister && <small>Use at least 8 characters.</small>}
        </label>
        <ErrorMessage message={error} />
        <button className="button auth-submit" type="submit" disabled={loading}>
          {loading ? 'Please wait...' : isRegister ? 'Create account' : 'Sign in'}
        </button>
      </form>
      <p className="auth-switch">
        {isRegister ? 'Already have an account?' : 'New to the research workspace?'}
        {' '}
        <Link to={isRegister ? '/login' : '/register'}>{isRegister ? 'Sign in' : 'Create an account'}</Link>
      </p>
    </section>
  </main>
}
