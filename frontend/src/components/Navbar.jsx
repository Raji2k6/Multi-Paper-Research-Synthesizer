import { Link } from 'react-router-dom'
import BrandMark from './BrandMark'

export default function Navbar({ user, onLogout }) {
  return <header className="topbar"><Link className="brand" to="/"><BrandMark /><span className="brand-title">PaperFusion AI<span className="brand-subtitle">Your research, connected</span></span></Link><div className="topbar-actions"><span className="topbar-note">From papers to connected insights</span>{user && <><span className="account-name">{user.name}</span><button className="button secondary logout-button" type="button" onClick={onLogout}>Sign out</button></>}</div></header>
}