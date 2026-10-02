import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import SourceCard from './SourceCard'

export default function SynthesisResult({ result }) {
  const uniqueSources = [...new Map((result.sources || []).map((source) => [`${source.document_id}-${source.page}`, source])).values()]
  return <div className="panel result-panel">
    <div className="result-heading">
      <div>
        <span className="eyebrow">Analysis complete</span>
        <h2>Research synthesis</h2>
      </div>
      <span className="summary-pill">{result.documents_analyzed} papers analyzed</span>
    </div>
    <section className="synthesis-section">
      <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]}>{result.answer}</ReactMarkdown></div>
    </section>
    {uniqueSources.length > 0 && <section className="synthesis-section">
      <h2>Sources</h2>
      <div className="source-list">{uniqueSources.map((source) => <SourceCard key={`${source.document_id}-${source.page}`} source={source} />)}</div>
    </section>}
  </div>
}