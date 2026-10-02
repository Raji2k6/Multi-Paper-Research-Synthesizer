import { ArrowUpRight, BookOpenCheck, FileText, FileUp, MessageSquare, Network, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'

const workflows = [
  { step: '01 / BUILD YOUR LIBRARY', title: 'Bring in your papers', description: 'Add PDFs and turn them into a searchable source library.', icon: FileUp, to: '/documents' },
  { step: '02 / EXPLORE THE EVIDENCE', title: 'Ask better questions', description: 'Get answers grounded in passages from your papers.', icon: MessageSquare, to: '/chat' },
  { step: '03 / CONNECT THE FINDINGS', title: 'Compare across studies', description: 'Surface shared results, differences, and contradictions.', icon: Network, to: '/synthesis' },
]

function PaperArtwork() {
  return <div className="hero-art" aria-hidden="true">
    <div className="paper-visual back"><div className="paper-top"><FileText size={15} /><span>Study 02</span></div><div className="paper-title">Methods and outcomes in recent clinical research</div><div className="paper-rule" /><div className="paper-rule short" /><div className="paper-highlight" /><div className="paper-rule" /></div>
    <div className="paper-visual front"><div className="paper-top"><FileText size={15} /><span>Study 01</span></div><div className="paper-title">A systematic review of evidence and impact</div><div className="paper-rule" /><div className="paper-highlight" /><div className="paper-rule" /><div className="paper-rule short" /></div>
    <div className="visual-tag"><BookOpenCheck size={16} /> Evidence, connected</div>
  </div>
}

export default function Dashboard({ documentCount }) {
  return <div className="dashboard">
    <section className="dashboard-hero">
      <div className="hero-copy">
        <span className="eyebrow">PaperFusion AI · Research workspace</span>
        <h1>Find the connections between your papers.</h1>
        <p>One place to organize studies, ask grounded questions, and see how the evidence fits together.</p>
        <div className="hero-actions">
          <Link className="button" to="/documents"><FileUp size={15} /> Add papers <ArrowUpRight size={14} /></Link>
          <Link className="button secondary" to="/synthesis"><Sparkles size={15} /> Compare findings</Link>
        </div>
      </div>
      <PaperArtwork />
    </section>
    <section className="dashboard-summary" aria-label="Workspace at a glance">
      <div className="summary-card"><div className="summary-icon"><FileText size={19} /></div><div><strong>{documentCount}</strong><span>{documentCount === 1 ? 'paper in your library' : 'papers in your library'}</span></div></div>
      <div className="summary-card"><div className="summary-icon"><MessageSquare size={19} /></div><div><strong>Cited answers</strong><span>Explore with source passages</span></div></div>
      <div className="summary-card"><div className="summary-icon"><Network size={19} /></div><div><strong>Cross-paper view</strong><span>See patterns across studies</span></div></div>
    </section>
    <div className="dashboard-section-heading"><h2>Your research, step by step</h2><span>Three tools. One connected workflow.</span></div>
    <section className="workflow-grid">
      {workflows.map(({ step, title, description, icon: Icon, to }) => <Link className="workflow-card" to={to} key={to}>
        <div className="workflow-card-head"><div className="summary-icon"><Icon size={18} /></div><span className="workflow-step">{step}</span></div>
        <h3>{title}</h3><p>{description}</p>
      </Link>)}
    </section>
  </div>
}