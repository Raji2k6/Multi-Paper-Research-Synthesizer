import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Navbar() {
  return <header className="topbar"><Link className="brand" to="/"><span className="brand-mark"><BookOpen size={19} /></span><span className="brand-title">Multi-Paper Research Synthesizer<span className="brand-subtitle">AI-powered research analysis</span></span></Link><span className="topbar-note">A focused workspace for better literature review</span></header>
}