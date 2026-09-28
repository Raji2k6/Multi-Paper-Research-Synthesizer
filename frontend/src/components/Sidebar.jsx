import { FileText, Home, MessageSquare, Network } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [{ to: '/', label: 'Dashboard', icon: Home }, { to: '/documents', label: 'Documents', icon: FileText }, { to: '/chat', label: 'Research Chat', icon: MessageSquare }, { to: '/synthesis', label: 'Multi-Paper Synthesis', icon: Network }]

export default function Sidebar() {
  return <aside className="sidebar"><div className="nav-label">Workspace</div>{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}><Icon size={17} /><span>{label}</span></NavLink>)}</aside>
}