import { FileText, Home, MessageSquare, Network, ShieldCheck } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [{ to: '/', label: 'Overview', icon: Home }, { to: '/documents', label: 'Paper library', icon: FileText }, { to: '/chat', label: 'Ask your papers', icon: MessageSquare }, { to: '/synthesis', label: 'Compare papers', icon: Network }]

export default function Sidebar() {
  return <aside className="sidebar"><div className="nav-label">Your workspace</div>{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}><Icon size={17} /><span>{label}</span></NavLink>)}<div className="sidebar-foot"><ShieldCheck size={17} /><p><strong>Private by design</strong>Your library stays yours</p></div></aside>
}